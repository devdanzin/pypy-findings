"""PyPy 3.11 (7.3.23): a spent `itertools.zip_longest` segfaults any BULK consumer.

    $ pypy3.11 -c '
    import itertools
    z = itertools.zip_longest([], [1, 2, 3])
    next(z)
    list(z)'
    Segmentation fault (core dumped)

Three lines, no threads, no address-space limit, no fuzzer scaffolding, 12/12. CPython
returns `[]`: a spent zip_longest is simply empty there.

THE DEFECT

`W_ZipLongest._fetch` stores None into `self.iterators_w[i]` when sub-iterator i raises
StopIteration while others are still active:

    pypy/module/itertools/interp_itertools.py:638-642
        self.active -= 1
        if self.active <= 0:
            raise                      # last one: propagate, do NOT null
        self.iterators_w[index] = None # not the last one: retire this sub-iterator

`W_ZipLongest.iterator_greenkey` then reads index 0 back with no None check:

    pypy/module/itertools/interp_itertools.py:677-682
        def iterator_greenkey(self, space):
            # XXX in theory we should tupleize the greenkeys of all the
            # sub-iterators, but much more work
            if len(self.iterators_w) > 0:
                return space.iterator_greenkey(self.iterators_w[0])   # <-- may be None
            return None

`space.iterator_greenkey(None)` calls a method on a null pointer in translated RPython.

WHICH CONSUMERS, AND WHY THAT SPLIT IS THE DIAGNOSIS

`iterator_greenkey` is consulted by the space-level BULK UNPACK path (`_do_extend_from_iterable`
in objspace/std/listobject.py and its set / dict / unicode counterparts), which is why the
crash tracks the consumer rather than the object:

    faults    list  tuple  set  frozenset  dict  sorted  min  list.extend  [*z]
    clean     for-loop   next()   [x for x in z]   sum(1 for _ in z)   "".join(genexp)
              repr()     z.__reduce__()

Everything in the clean row goes through the FOR_ITER bytecode, which never asks for a
greenkey. Nothing about the zip_longest differs between the two rows.

A MECHANISM THAT PREDICTS, AND SEVEN PREDICTIONS THAT HOLD

Only index 0 is read, and an entry is nulled only when its sub-iterator is NOT the last one
alive. So the crash needs the FIRST argument to be among the first exhausted -- which is a
falsifiable claim about arguments, not a hedge:

    zip_longest([1,2,3], range(10))        first arg exhausts first   SIGSEGV
    zip_longest(range(10), [1,2,3])        first arg outlives         clean
    zip_longest([1,2,3], [4,5,6])          equal lengths              SIGSEGV
    zip_longest([1,2,3])                   single argument            clean
    zip_longest([1], range(5), range(9))   first arg shortest         SIGSEGV
    zip_longest(range(9), [1], range(5))   first arg longest          clean
    zip_longest()                          no arguments               clean

The two clean multi-argument cases are clean for the same reason: when `active` reaches 0 the
`raise` in `_fetch` happens BEFORE the assignment, so the last surviving entry is never nulled.
The single-argument case is that reason with one iterator.

A COPIED INVARIANT, NOT A FORGOTTEN GUARD

The identical method body -- down to the same `XXX in theory we should tupleize` comment --
also sits on `W_Map` and `W_Zip` in pypy/module/__builtin__/functional.py:875 and :1093,
where it is CORRECT: neither ever stores None into `iterators_w`. Both were checked on the
same double-consume below and are clean.

`W_ZipLongest.iterator_greenkey` arrived by copy in 6bd66bda3c ("make W_ZipLongest stop
subclassing from W_Map as well", 2022-06-11), long after the nulling it invalidates, which has
been in `_fetch` since izip_longest was first implemented. The class already knows the entry
can be None -- `descr_reduce`, a dozen lines above the faulting read, writes
`iterator if iterator is not None else space.newtuple([])`.

By git history the read has been reachable since release-pypy3.9-v7.3.10 (28 release tags);
only 7.3.23 was tested here. The file is byte-identical between the 7.3.23 tag and main at
fe2af5843a (2026-08-18) apart from an unrelated `tee` change.

FIX

A None check at the read, matching what `descr_reduce` already does -- e.g. return the first
entry that is not None, or fall back to `space.type(self)` when index 0 has been retired.
"""

import itertools
import subprocess
import sys

ARG_CASES = [
    ("zip_longest([1,2,3], range(10))", "itertools.zip_longest([1,2,3], range(10))", True),
    ("zip_longest(range(10), [1,2,3])", "itertools.zip_longest(range(10), [1,2,3])", False),
    ("zip_longest([1,2,3], [4,5,6])", "itertools.zip_longest([1,2,3], [4,5,6])", True),
    ("zip_longest([1,2,3])", "itertools.zip_longest([1,2,3])", False),
    ("zip_longest([1], range(5), range(9))", "itertools.zip_longest([1], range(5), range(9))", True),
    ("zip_longest(range(9), [1], range(5))", "itertools.zip_longest(range(9), [1], range(5))", False),
    ("zip_longest()", "itertools.zip_longest()", False),
]

CONSUMERS = [
    ("list", "list(z)", True), ("tuple", "tuple(z)", True), ("set", "set(z)", True),
    ("frozenset", "frozenset(z)", True), ("dict", "dict(z)", True), ("sorted", "sorted(z)", True),
    ("min", "min(z, default=None)", True), ("list.extend", "[].extend(z)", True),
    ("[*z]", "[*z]", True),
    ("for loop", "[None for _ in z]", False), ("next", "next(z, None)", False),
    ("listcomp", "[x for x in z]", False), ("genexp sum", "sum(1 for _ in z)", False),
    ("join genexp", "''.join(str(x) for x in z)", False), ("repr", "repr(z)", False),
    ("__reduce__", "z.__reduce__()", False),
]

SIBLINGS = [
    ("itertools.zip_longest", "itertools.zip_longest([1,2,3], range(10))", True),
    ("builtins.zip", "zip([1,2,3], range(10))", False),
    ("builtins.map", "map(lambda *a: a, [1,2,3], range(10))", False),
]

CHILD = """
import itertools
z = {expr}
try: list(z)
except Exception: pass
try: {consumer}
except Exception: pass
print("survived")
"""


def faults(expr, consumer="list(z)"):
    p = subprocess.run([sys.executable, "-c", CHILD.format(expr=expr, consumer=consumer)],
                       capture_output=True, stdin=subprocess.DEVNULL)
    return p.returncode == -11


def section(title, rows, run):
    print(title)
    bad = 0
    for label, expected, got in ((lbl, exp, run(*rest)) for lbl, *rest, exp in rows):
        flag = "" if got == expected else "   <-- NOT AS DOCUMENTED"
        if got != expected:
            bad += 1
        print("  %-38s %-9s %s%s" % (label, "SIGSEGV" if got else "clean",
                                     "(expected %s)" % ("SIGSEGV" if expected else "clean"), flag))
    print()
    return bad


def main():
    print("%s %s\n" % (sys.implementation.name, sys.version.split()[0]))
    mismatches = 0
    mismatches += section(
        "(1) which ARGUMENTS fault -- only when index 0 is among the first exhausted:",
        ARG_CASES, lambda expr: faults(expr))
    mismatches += section(
        "(2) which CONSUMERS fault -- the bulk-unpack path, not FOR_ITER:",
        [(lbl, "itertools.zip_longest([1,2,3], range(10))", code, exp)
         for lbl, code, exp in CONSUMERS],
        lambda expr, consumer: faults(expr, consumer))
    mismatches += section(
        "(3) the two SIBLINGS with the byte-identical iterator_greenkey body:",
        SIBLINGS, lambda expr: faults(expr))

    if mismatches:
        print("%d case(s) did not match the record -- the analysis needs revisiting." % mismatches)
        return 2
    if any(faults(e) for _, e, exp in ARG_CASES if exp):
        print("A spent zip_longest segfaults every bulk consumer, and only where the\n"
              "iterators_w[0]-is-None mechanism says it should.")
        return 1
    print("No faults anywhere. On CPython this is the expected result.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
