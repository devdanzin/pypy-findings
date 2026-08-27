# FUSIL_BOILERPLATE_START

# Record a Python-level backtrace if the target dies on a fatal signal.
# Without this a SIGSEGV/SIGABRT leaves stdout ending at the last call line
# with no indication of WHERE it died. That is worst for exactly the crashes
# that need it most -- rare, threaded, load-dependent ones that do not
# reproduce afterwards -- so capturing at crash time is the only chance.
# Enabled first, before any other import, so a crash in the prelude is caught
# too. Guarded: not every target interpreter ships a working faulthandler.
try:
    import faulthandler as _fusil_faulthandler
    _fusil_faulthandler.enable()
except Exception:
    pass
from gc import collect
# NOTE: do NOT import `random` (the function) here -- it would shadow the
# `random` module that embedded tricky-object code imports and uses as
# `random.randint(...)`, turning those calls into AttributeError at module load.
from random import choice, randint, sample, seed
from sys import stderr, path as sys_path
from os.path import dirname
import ast
import inspect
import io
import math
import operator
import time
import sys
from threading import Thread
from unittest.mock import MagicMock
import asyncio
seed(521247920)

try:
    from string.templatelib import Interpolation, Template
except ImportError:
    pass
print("Importing target module: multiprocessing.popen_fork", file=stderr)
try:
    import multiprocessing.popen_fork
except ImportError as _fusil_import_error:
    print("FUSIL: target module multiprocessing.popen_fork not importable (skipping):", repr(_fusil_import_error), file=stderr)
    raise SystemExit(0)

TRIVIAL_TYPES = {int, str, float, bool, bytes, tuple, list, dict, set, type(None),}
def skip_trivial_type(obj_instance_or_class):
    if type(obj_instance_or_class) in TRIVIAL_TYPES:
        return True
    return False


_FUSIL_METHOD_BLACKLIST = frozenset({'__class__', '__enter__', '__imul__', '__ipow__', '__mul__', '__pow__', '__rmul__', '_acquire_lock', '_acquire_restore', '_handle_request_noblock', '_randbelow', '_randbelow_with_getrandbits', '_read', '_rehash', '_run_once', '_serve', '_shutdown', 'accept', 'acquire', 'acquire_lock', 'cmdloop', 'copyfileobj', 'get', 'get_request', 'handle_request', 'handle_request_noblock', 'prefix', 'raise_signal', 'repeat', 'run_forever', 'select', 'serve_forever', 'shutdown', 'sleep', 'test', 'tri', 'tril_indices', 'wait', 'zfill'})

import sys
from abc import ABCMeta
from collections import Counter, OrderedDict, deque
from queue import Queue
from random import randint
from string import printable

try:
    from _decimal import Decimal

    has__decimal = True
except ImportError:
    from decimal import Decimal

    has__decimal = False

sequences = [Queue, deque, frozenset, list, set, str, tuple]
bytes_ = [bytearray, bytes]
numbers = [Decimal, complex, float, int]
dicts = [Counter, OrderedDict, dict]
# dicts = [OrderedDict, dict]
bases = sequences + bytes_ + numbers + dicts + [object]

large_num = 2**64


class WeirdBase(ABCMeta):
    def __hash__(self):
        return randint(0, large_num)

    def __eq__(self, other):
        return False


weird_instances = dict()
weird_classes = dict()
for cls in bases:

    class weird_cls(cls, metaclass=WeirdBase):
        def add(self, *args, **kwargs):
            pass

        append = clear = close = write = sort = reversed = add

        def encode(self, *args, **kwargs):
            return b""

        def decode(self, *args, **kwargs):
            return ""

        format = getvalue = join = read = replace = strip = rstrip = decode

        def get(self, *args, **kwargs):
            return self

        open = pop = update = get

        def readlines(self, *args, **kwargs):
            return [""]

        rsplit = split = partition = rpartition = readlines

        def items(self):
            return {}.items()

        def keys(self):
            return {}.keys()

        def values(self):
            return {}.values()

    weird_cls.__name__ = f"weird_{cls.__name__}"
    weird_instances[f"weird_{cls.__name__}_empty"] = weird_cls()
    weird_classes[f"weird_{cls.__name__}"] = weird_cls

tricky_strs = (
    chr(0),
    chr(127),
    chr(255),
    chr(0x10FFFF),
    "𝒜",
    "\\x00" * 10,
    "A" * (2**16),
    "💻" * 2**10,
)

# We cannot create a Decimal larger than 10 ** 4300 with _pydecimal, only with _decimal
max_str_digits_adjustment = 1 if has__decimal else -1
# default_max_str_digits is CPython 3.11+; fall back to its 4300 default on interpreters
# (older CPython, some PyPy) that don't expose it so this boilerplate stays importable.
_default_max_str_digits = getattr(sys, "int_info", None)
_default_max_str_digits = getattr(_default_max_str_digits, "default_max_str_digits", 4300)
big_int_for_decimal = 10 ** (_default_max_str_digits + max_str_digits_adjustment)

for cls in sequences:
    weird_instances[f"weird_{cls.__name__}_single"] = weird_classes[f"weird_{cls.__name__}"]("a")
    weird_instances[f"weird_{cls.__name__}_range"] = weird_classes[f"weird_{cls.__name__}"](
        range(20)
    )
    weird_instances[f"weird_{cls.__name__}_types"] = weird_classes[f"weird_{cls.__name__}"](bases)
    weird_instances[f"weird_{cls.__name__}_printable"] = weird_classes[f"weird_{cls.__name__}"](
        printable
    )
    weird_instances[f"weird_{cls.__name__}_special"] = weird_classes[f"weird_{cls.__name__}"](
        tricky_strs
    )
for cls in bytes_:
    weird_instances[f"weird_{cls.__name__}_bytes"] = weird_classes[f"weird_{cls.__name__}"](
        b"abcdefgh_" * 10
    )
for cls in numbers:
    weird_instances[f"weird_{cls.__name__}_sys_maxsize"] = weird_classes[f"weird_{cls.__name__}"](
        sys.maxsize
    )
    weird_instances[f"weird_{cls.__name__}_sys_maxsize_minus_one"] = weird_classes[
        f"weird_{cls.__name__}"
    ](sys.maxsize - 1)
    weird_instances[f"weird_{cls.__name__}_sys_maxsize_plus_one"] = weird_classes[
        f"weird_{cls.__name__}"
    ](sys.maxsize + 1)
    weird_instances[f"weird_{cls.__name__}_neg_sys_maxsize"] = weird_classes[
        f"weird_{cls.__name__}"
    ](-sys.maxsize)
    weird_instances[f"weird_{cls.__name__}_2**63-1"] = weird_classes[f"weird_{cls.__name__}"](
        2**63 - 1
    )
    weird_instances[f"weird_{cls.__name__}_2**63"] = weird_classes[f"weird_{cls.__name__}"](2**63)
    weird_instances[f"weird_{cls.__name__}_2**63+1"] = weird_classes[f"weird_{cls.__name__}"](
        2**63 + 1
    )
    weird_instances[f"weird_{cls.__name__}_-2**63+1"] = weird_classes[f"weird_{cls.__name__}"](
        -(2**63) + 1
    )
    weird_instances[f"weird_{cls.__name__}_-2**63"] = weird_classes[f"weird_{cls.__name__}"](
        -(2**63)
    )
    weird_instances[f"weird_{cls.__name__}_-2**63-1"] = weird_classes[f"weird_{cls.__name__}"](
        -(2**63) - 1
    )
    weird_instances[f"weird_{cls.__name__}_2**31-1"] = weird_classes[f"weird_{cls.__name__}"](
        2**31 - 1
    )
    weird_instances[f"weird_{cls.__name__}_2**31"] = weird_classes[f"weird_{cls.__name__}"](2**31)
    weird_instances[f"weird_{cls.__name__}_2**31+1"] = weird_classes[f"weird_{cls.__name__}"](
        2**31 + 1
    )
    weird_instances[f"weird_{cls.__name__}_-2**31+1"] = weird_classes[f"weird_{cls.__name__}"](
        -(2**31) + 1
    )
    weird_instances[f"weird_{cls.__name__}_-2**31"] = weird_classes[f"weird_{cls.__name__}"](
        -(2**31)
    )
    weird_instances[f"weird_{cls.__name__}_-2**31-1"] = weird_classes[f"weird_{cls.__name__}"](
        -(2**31) - 1
    )
    if cls not in (float, complex) and hasattr(sys, "int_info"):
        weird_instances[f"weird_{cls.__name__}_10**default_max_str_digits+1"] = weird_classes[
            f"weird_{cls.__name__}"
        ](big_int_for_decimal)
for cls in dicts:
    weird_instances[f"weird_{cls.__name__}_basic"] = weird_classes[f"weird_{cls.__name__}"](
        {a: a for a in range(100)}
    )
    weird_instances[f"weird_{cls.__name__}_tricky_strs"] = weird_classes[f"weird_{cls.__name__}"](
        {a: a for a in tricky_strs}
    )


# Class with a __del__ side effect to attack the JIT optimizer
class FrameModifier:
    def __init__(self, var_name, new_value):
        # Store the name of the variable to target and its new value.
        self.var_name = var_name
        self.new_value = new_value
        # Announce creation for debugging the generated script
        print(f"  [FrameModifier created to target '{self.var_name}']", file=sys.stderr)

    def __del__(self):
        try:
            # On destruction, get the calling frame (1 level up).
            frame = sys._getframe(1)
            # Maliciously modify the local variable in that frame.
            print(
                f"  [Side Effect] In __del__: Modifying '{self.var_name}' to {self.new_value!r}",
                file=sys.stderr,
            )
            if self.var_name in frame.f_locals:
                frame.f_locals[self.var_name] = self.new_value
            elif (
                self.var_name.split(".")[0] in frame.f_locals and self.var_name.count(".") == 1
            ):  # instance_or_class.attribute
                instance_or_class_str, attr_str = self.var_name.split(".")
                setattr(frame.f_locals[instance_or_class_str], attr_str, self.new_value)
            else:  # module.instance_or_class.attribute
                module_str, instance_or_class_str, attr_str = self.var_name.split(".")
                instance_or_class = getattr(frame.f_locals[module_str], instance_or_class_str)
                setattr(instance_or_class, attr_str, self.new_value)
        except Exception as e:
            # Frame inspection can be tricky; don't crash in __del__.
            print(f"  [Side Effect] Error in FrameModifier.__del__: {e}", file=sys.stderr)


import abc
import builtins
import collections.abc
import itertools
import types
import typing
from functools import reduce
from operator import or_

abc_types = [cls for cls in abc.__dict__.values() if isinstance(cls, type)]
builtins_types = [cls for cls in builtins.__dict__.values() if isinstance(cls, type)]
collections_abc_types = [cls for cls in collections.abc.__dict__.values() if isinstance(cls, type)]
collections_types = [cls for cls in collections.__dict__.values() if isinstance(cls, type)]
itertools_types = [cls for cls in itertools.__dict__.values() if isinstance(cls, type)]
types_types = [cls for cls in types.__dict__.values() if isinstance(cls, type)]
typing_types = [cls for cls in typing.__dict__.values() if isinstance(cls, type)]

all_types = (
    abc_types
    + builtins_types
    + collections_abc_types
    + collections_types
    + itertools_types
    + types_types
    + typing_types
)
all_types = [t for t in all_types if not (isinstance(t, type) and issubclass(t, BaseException))]
big_union = reduce(or_, all_types, int)


import inspect
import types

tricky_cell = types.CellType(None)
tricky_simplenamespace = types.SimpleNamespace(dummy=None, cell=tricky_cell)
tricky_simplenamespace.dummy = tricky_simplenamespace
try:
    tricky_capsule = types.CapsuleType
except AttributeError:
    tricky_capsule = None
tricky_module = types.ModuleType("tricky_module", "docs")
tricky_module2 = types.ModuleType("tricky_module2\\x00", "docs\\x00")
try:
    tricky_genericalias = types.GenericAlias(list, (int,))
except AttributeError:
    tricky_genericalias = None

tricky_dict = {}
if tricky_capsule:
    tricky_dict[tricky_capsule] = tricky_cell
if tricky_module:
    tricky_dict[tricky_module] = tricky_genericalias
tricky_dict["tricky_dict"] = tricky_dict
tricky_mappingproxy = types.MappingProxyType(tricky_dict)


def tricky_function(*args, **kwargs):
    if len(args) > 150:
        raise RecursionError("Fuzzer controlled depth")
    a = 1

    def b(x=a):
        v = x
        return v

    return tricky_function(*(args + (1,)), **kwargs)


tricky_lambda = lambda *args, **kwargs: tricky_lambda(*args, **kwargs)
tricky_classmethod = classmethod(tricky_lambda)
tricky_staticmethod = staticmethod(tricky_lambda)
tricky_property = property(tricky_lambda)
tricky_code = tricky_lambda.__code__
tricky_closure = tricky_function.__code__.co_freevars
tricky_classmethod_descriptor = types.ClassMethodDescriptorType  # This is the type itself


class TrickyDescriptor:
    def __get__(self, obj, objtype=None):
        return self

    def __set__(self, obj, value):
        try:
            obj.__dict__["_value_descriptor"] = value
        except AttributeError:
            pass

    def __delete__(self, obj):
        try:
            del obj.__dict__["_value_descriptor"]
        except (AttributeError, KeyError):
            pass


class TrickyMeta(type):
    @property
    def __signature__(self):
        raise AttributeError("Signature denied by TrickyMeta")

    def __mro_entries__(self, bases):
        return (object,)
        # return super().__mro_entries__(bases)


class TrickyClass(metaclass=TrickyMeta):
    tricky_descriptor = TrickyDescriptor()

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, *args, **kwargs):
        self._value_init = None

    def __getattr__(self, name):
        if name == "crash_on_getattr":
            raise ValueError("getattr manipulated")
        return self


tricky_instance = TrickyClass()
try:
    tricky_frame = inspect.currentframe()
    if tricky_frame:  # currentframe() can be None
        # tricky_frame.f_builtins.update(tricky_dict)
        tricky_frame.f_globals.update(tricky_dict)
        tricky_frame.f_locals.update(tricky_dict)
# Writing f_locals is a CPython frame detail (PEP 667 in 3.13); on interpreters where
# it is a read-only snapshot the .update() can raise TypeError/AttributeError, not just
# RuntimeError -- catch broadly so this best-effort frame pollution never aborts the script.
except Exception:
    tricky_frame = None


try:
    1 / 0
except ZeroDivisionError as e:
    tricky_traceback = e.__traceback__
else:
    tricky_traceback = None


# tricky_generator = (x for x in itertools.count())
tricky_list_with_cycle = [[]] * 6 + []
tricky_list_with_cycle[0].append(tricky_list_with_cycle)
tricky_list_with_cycle[-1].append(tricky_list_with_cycle)
tricky_list_with_cycle.append(tricky_list_with_cycle)
if tricky_list_with_cycle[0] and tricky_list_with_cycle[0][0] is tricky_list_with_cycle:
    tricky_list_with_cycle[0][0].append(tricky_list_with_cycle)


# --- Recursion-shape probes: map the unguarded-native-recursion crash class (RustPython #2796).
# Each object re-enters a protocol on a PARTNER object, so the recursion crosses object boundaries
# (mutual recursion, harder to short-circuit than plain self-recursion). CPython raises
# RecursionError on the protocol call; an interpreter without a recursion guard on that native
# path overflows its C/Rust stack -> segfault. Construction is cheap -- the recursion fires only
# when the fuzzer exercises the named protocol (hash/eq/getitem/iter/repr/call) on the object.
class _TrickyRecur:
    def __init__(self, name):
        self.name = name
        self.partner = self  # rebound to a partner below for mutual recursion

    def __hash__(self):
        return hash(self.partner)

    def __eq__(self, other):
        return self.partner == other

    def __getitem__(self, key):
        return self.partner[key]

    def __iter__(self):
        return iter(self.partner)

    def __repr__(self):
        return repr(self.partner)

    def __call__(self, *args, **kwargs):
        return self.partner(*args, **kwargs)


tricky_recur_a = _TrickyRecur("a")
tricky_recur_b = _TrickyRecur("b")
tricky_recur_a.partner = tricky_recur_b
tricky_recur_b.partner = tricky_recur_a

# Deep generic-alias nesting list[list[...list[T]...]] bottomed on a TypeVar so the parameter walk
# actually recurses to collect it -- exercises the genericalias parameter-walk native path
# (RustPython segfaulted in genericalias::make_parameters_from_slice). Bounded depth so construction
# + a CPython repr stay well under the recursion limit; the native walk (and __getitem__
# substitution) is the target. Falls back to a plain nested alias if TypeVar is unavailable.
try:
    from typing import TypeVar as _TrickyTypeVar

    _TrickyGAT = _TrickyTypeVar("_TrickyGAT")
    _tricky_ga = _TrickyGAT
except Exception:
    _tricky_ga = list
try:
    for _ in range(80):
        _tricky_ga = list[_tricky_ga]
    tricky_deep_genericalias = _tricky_ga
except Exception:
    tricky_deep_genericalias = None


"""Exception-bomb objects: the protocol-level analogue of the OOM (allocation-failure) mode.

The OOM allocator hook makes *allocations* fail deterministically; a bomb object makes a
*dunder callback* fail -- exercising the large class of C code that calls a Python protocol
slot (``__hash__``, ``__eq__``, ``__index__``, ``__len__``, ``__iter__``, ``__repr__``, ...)
and then does an unguarded ``PyErr_Clear()`` or assumes the slot succeeded.

Two knobs, both randomised at construction so repeated use across a run walks a wide slice of
program state (the windowed-failure insight of the OOM sequence mode applied to protocol slots):

* **delay** — succeed a random number of times, *then* raise. Delay 0 means "raise on first
  use"; delay N means "corrupt/observe state for N calls, then fail" (the cross-call
  "succeeded during insert, fails during lookup" shape that surfaces swallowed exceptions).
* **exception** — the targeted bombs raise ``MemoryError`` (the highest-value target for the
  unguarded-error-path bug class), while ``SuperBomb`` raises a *random* exception from a wide
  set: spray-and-pray coverage of every protocol slot at once.

This module is embedded verbatim into generated fuzzing scripts, so it must stay
self-contained (only ``random`` + builtins) and import-safe.
"""

# Import the random *module* under a private alias. The generated script's boilerplate does
# ``from random import ..., random``, which rebinds the bare name ``random`` to the random()
# *function*; a private alias keeps this embedded code reaching the module's randint/choice.
import random as _bomb_random

# Weighted toward MemoryError (the unguarded-PyErr_Clear / swallowed-error bug class) but
# spanning the exceptions C code is most likely to mishandle when a slot raises unexpectedly.
_BOMB_EXCEPTIONS = (
    MemoryError,
    MemoryError,
    MemoryError,
    RecursionError,
    OverflowError,
    ValueError,
    TypeError,
    RuntimeError,
    KeyError,
    IndexError,
    StopIteration,
    SystemError,
    # Only Exception subclasses belong here. BaseException types (KeyboardInterrupt,
    # SystemExit, GeneratorExit) escape the generated `except Exception` handlers, so a bomb
    # raising one aborts the whole session (SIGINT / nonzero exit) as a false crash rather
    # than exercising the target's error handling.
)


def _bomb_exc(exc=None):
    return exc if exc is not None else _bomb_random.choice(_BOMB_EXCEPTIONS)


class _BombBase:
    """Succeed a random ``delay`` (0..max_delay) times, then raise ``exc`` from armed slots."""

    def __init__(self, max_delay=3, exc=MemoryError):
        self._calls = 0
        self._delay = _bomb_random.randint(0, max_delay)
        self._exc = exc

    def _fire(self):
        self._calls += 1
        if self._calls > self._delay:
            raise _bomb_exc(self._exc)("fusil bomb")


class HashBomb(_BombBase):
    """__hash__ raises after the delay -- hits dict/set insert & lookup error paths."""

    def __hash__(self):
        self._fire()
        return 42

    def __eq__(self, other):
        return self is other


class EqBomb(_BombBase):
    """Comparison raises; stays hashable and looks sequence-ish to pass pre-checks."""

    def __eq__(self, other):
        self._fire()
        return NotImplemented

    def __ne__(self, other):
        self._fire()
        return NotImplemented

    def __hash__(self):
        return 0

    def __iter__(self):
        return iter(())

    def __len__(self):
        return 0


class IndexBomb(_BombBase):
    """Numeric coercion raises -- hits sequence-index / int-conversion error paths."""

    def __index__(self):
        self._fire()
        return 1

    def __int__(self):
        self._fire()
        return 1

    def __float__(self):
        self._fire()
        return 1.0


class LenBomb(_BombBase):
    """__len__ raises but __iter__ works -- length-then-iterate mismatch."""

    def __len__(self):
        self._fire()
        return 3

    def __iter__(self):
        return iter([1, 2, 3])


class LyingLen:
    """__len__ reports a huge size (over-allocation) but yields few items."""

    def __len__(self):
        return 1_000_000

    def __iter__(self):
        return iter([1, 2, 3])


class ReprBomb(_BombBase):
    """__repr__/__str__ raise -- hits error-formatting and logging paths in C."""

    def __repr__(self):
        self._fire()
        return "<ReprBomb>"

    __str__ = __repr__


class FailingIterator:
    """Yields a random few items, then raises mid-iteration (partial-mutation on
    extend/update/list()/dict-from-pairs)."""

    def __init__(self, max_items=4, exc=None):
        self._i = 0
        self._n = _bomb_random.randint(0, max_items)
        self._exc = exc

    def __iter__(self):
        return self

    def __next__(self):
        if self._i >= self._n:
            raise _bomb_exc(self._exc)("fusil iter bomb")
        self._i += 1
        return self._i


# --- Reentrant-mutation bombs: MUTATE the container mid-operation (not just raise) --------
#
# The exception bombs above make a protocol slot RAISE; these make it MUTATE the very
# container the running C operation is iterating -- the reentrancy / use-after-free class.
# When a C sequence/mapping routine borrows a container's internal storage (``ob_item`` array,
# hash-table ``entries``) and then calls back into Python -- to compare (``__eq__``/``__lt__``),
# hash (``__hash__``), or convert (``__index__``) an element -- clearing or resizing that
# container from inside the callback frees/reallocates the borrowed pointer mid-loop. Core
# CPython's own list/dict routines mostly re-check the size after each callback, but a great
# deal of C-EXTENSION code (and less-trodden CPython C paths) caches the raw pointer once and
# indexes it, so these objects are the protocol-slot analogue of an OOM injection aimed at the
# reentrancy error path rather than the allocation-failure one. The mutation is DELAYED a few
# calls (like the exception bombs) so a partially-consumed C loop is holding a live borrowed
# pointer when it fires, rather than emptying the container before the loop starts.


class _ClearParent:
    """An element that clears the container holding it, from inside a comparison/hash/index
    callback. Seeded into ``ReentrantClearList`` / ``ReentrantClearDict``; not used directly."""

    def __init__(self, parent, max_delay=2):
        self._parent = parent
        self._calls = 0
        self._delay = _bomb_random.randint(0, max_delay)

    def _maybe_pull(self):
        self._calls += 1
        if self._calls > self._delay:
            parent = self._parent
            try:
                parent.clear()
            except Exception:
                try:
                    del parent[:]
                except Exception:
                    pass

    def __eq__(self, other):
        self._maybe_pull()
        return False

    def __lt__(self, other):
        self._maybe_pull()
        return True

    def __gt__(self, other):
        self._maybe_pull()
        return False

    def __hash__(self):
        self._maybe_pull()
        return 0

    def __index__(self):
        self._maybe_pull()
        return 0

    __int__ = __index__


class ReentrantClearList(list):
    """A pre-armed ``list``: it contains a self-clearing element, so any C op that compares,
    hashes, or index-converts its items -- ``x in l`` / ``l.index(x)`` / ``l.sort()`` /
    ``min(l)`` / ``max(l)`` / ``set(l)`` / ``bytes(l)``, or a C-extension routine iterating a
    list argument -- can free the item array mid-loop (reentrant use-after-free)."""

    def __init__(self):
        super().__init__()
        head = _bomb_random.randint(1, 4)
        self.extend(range(head))
        self.append(_ClearParent(self))
        self.extend(range(head, head + _bomb_random.randint(2, 6)))


class ReentrantClearDict(dict):
    """A pre-armed ``dict``: a stored VALUE clears the dict from inside a comparison, so a C op
    that compares the mapping's values -- ``d == other`` / dict richcompare, or a C-extension
    routine walking a dict argument's values -- can free the entry table mid-walk."""

    def __init__(self):
        super().__init__()
        for i in range(_bomb_random.randint(1, 3)):
            self[i] = i
        self["_fusil_pull"] = _ClearParent(self)
        for i in range(_bomb_random.randint(1, 3)):
            self["k%d" % i] = i


class MutatingIterable:
    """A hostile iterable whose ``__length_hint__`` lies (huge / zero / negative) and whose
    iterator mutates its own backing store mid-iteration. C consumers that PRESIZE a buffer
    from the hint and then fill it by iterating -- ``list()`` / ``tuple()`` / ``bytes()`` /
    ``b"".join()`` / ``set()`` / ``[*it]`` / ``PySequence_Tuple`` / ``_PyList_Extend`` -- can
    over-read or write past the presized buffer when the real yield count disagrees."""

    def __init__(self):
        self._data = list(range(_bomb_random.randint(4, 16)))
        # A lie about the yield count: 0/1 (undersize -> grow path), -1 (negative -> the
        # unguarded-negative presize/ValueError vector), and a large-but-not-guaranteed-OOM
        # over-report (8 MB presize, not 8 TB -- a sprayed bomb must not just raise MemoryError).
        self._hint = _bomb_random.choice([0, 1, -1, 1 << 16, 1 << 20])

    def __length_hint__(self):
        return self._hint

    def __iter__(self):
        data = self._data

        def _gen():
            for i, value in enumerate(list(data)):
                if i == 1:
                    data.clear()
                elif i == 2:
                    data.extend(range(1 << 10))
                yield value

        return _gen()


# --- Stateful / lying bombs: the protocol slot SUCCEEDS but returns an INCONSISTENT answer ---
#
# The exception bombs raise; the reentrant bombs mutate a container. These lie *quietly*: a slot
# returns a value that is internally inconsistent across calls (or with a sibling slot), so C
# code that reads it once to size/plan and then trusts it -- preallocating a buffer from __len__,
# storing under a cached __hash__, specializing on the first element's type -- writes past the
# buffer, lands in the wrong hash bucket, or trips a type fast-path. The lie is DELAYED (like the
# other bombs) so the C routine has already committed to the first answer when it changes.


class GrowingLen:
    """__len__ under-reports on its first read (small presize) then reports a much larger size,
    while __getitem__ / __iter__ yield up to the larger count. C code that presizes a buffer from
    the first __len__ and then fills by index/iteration can write past it (the __len__-lies-small
    buffer-preallocation class; complements LyingLen, which only over-reports)."""

    def __init__(self):
        self._calls = 0
        self._small = _bomb_random.choice([0, 1, 2])
        self._big = _bomb_random.choice([64, 256, 4096])

    def __len__(self):
        self._calls += 1
        return self._small if self._calls <= 1 else self._big

    def __getitem__(self, index):
        if not isinstance(index, int) or index >= self._big or index < 0:
            raise IndexError(index)
        return index

    def __iter__(self):
        return iter(range(self._big))


class MutatingHash:
    """__hash__ is constant for a few calls -- long enough to be stored as a dict/set key -- then
    starts returning different values, violating hash-constancy while the object is a live key.
    A C hash table that cached the original hash now finds the key in the wrong bucket (lookup
    miss / KeyError, or a corrupted probe sequence in a less-hardened C-extension mapping)."""

    def __init__(self):
        self._calls = 0
        self._delay = _bomb_random.randint(1, 3)

    def __hash__(self):
        self._calls += 1
        if self._calls <= self._delay:
            return 0
        return _bomb_random.randrange(1 << 60)

    def __eq__(self, other):
        return self is other


class TypeFlipIterator:
    """Yields a consistent type (ints) for a few items, then flips to an incompatible type
    (str / None / float / a bare object) mid-stream, feeding C reducers that may specialize on
    the first element's type -- max() / min() / sum() / sorted() / bytes() / b"".join() / heapq --
    a wrong type after the fast-path has committed."""

    def __init__(self):
        self._i = 0
        self._n = _bomb_random.randint(2, 8)
        self._flip = _bomb_random.choice(["str", "none", "float", "obj"])

    def __iter__(self):
        return self

    def __next__(self):
        self._i += 1
        if self._i > self._n + 4:
            raise StopIteration
        if self._i <= self._n:
            return self._i  # a consistent run of ints
        return {"str": "x", "none": None, "float": 1.5, "obj": object()}[self._flip]


# --- Lying-equality bombs: hashable + storable, but == / identity lie -------------------------
#
# The stateful/lying bombs above lie about size/type; these lie about EQUALITY. They are cheap
# to hash and store (a stable, colliding hash) so a C container accepts them as a key/member,
# but their __eq__ then contradicts identity -- claiming equal to a value they are not, or giving
# a different answer on each call. C code that assumes `a == b` implies interchangeability, caches
# a slot after one comparison, or maintains its own hash table (a C-extension mapping) can probe
# the wrong bucket, double-store, or read a stale entry. On core dict/set this desyncs values;
# in a less-hardened C-extension container it can corrupt the table.


class LyingEq:
    """Hashes like the int ``1`` (a deliberate collision) and claims __eq__ equality with 1 and
    every small int, and __index__/__int__ return 1 -- yet it is a distinct object that is not 1.
    Used as a dict key / set member / sequence index it desyncs "equal-but-not-identical": stored
    and found under hash(1), but not actually interchangeable with the ints it claims to equal."""

    def __eq__(self, other):
        return other == 1 or (isinstance(other, int) and -5 <= other <= 256)

    def __hash__(self):
        return hash(1)

    def __index__(self):
        return 1

    __int__ = __index__


class ShiftyEq:
    """__eq__ flips its answer every few calls, so a single C routine that compares this object
    more than once (insert-then-lookup in a hash table, a membership scan, a sort) sees the
    equality relation change underneath it. __hash__ stays constant so it remains storable."""

    def __init__(self):
        self._calls = 0
        self._period = _bomb_random.randint(2, 4)

    def __eq__(self, other):
        self._calls += 1
        return (self._calls // self._period) % 2 == 0

    def __hash__(self):
        return 0


# --- SuperBomb: every protocol slot is a landmine ----------------------------------------
#
# Spray-and-pray. A metaclass installs a raising method for a broad set of dunders; each one
# raises a random exception, either on first use or after a per-instance random delay. The
# attribute/lifecycle dunders (__init__/__new__/__getattribute__/__setattr__/__del__/...) are
# deliberately left working so the object can be constructed and passed around to reach deep
# call sites before it detonates.

_SUPERBOMB_DUNDERS = (
    "__hash__",
    "__eq__",
    "__ne__",
    "__lt__",
    "__le__",
    "__gt__",
    "__ge__",
    "__call__",
    "__len__",
    "__length_hint__",
    "__bool__",
    "__contains__",
    "__int__",
    "__float__",
    "__index__",
    "__complex__",
    "__round__",
    "__trunc__",
    "__repr__",
    "__str__",
    "__format__",
    "__bytes__",
    "__fspath__",
    "__iter__",
    "__next__",
    "__reversed__",
    "__getitem__",
    "__setitem__",
    "__delitem__",
    "__missing__",
    "__add__",
    "__radd__",
    "__iadd__",
    "__sub__",
    "__rsub__",
    "__mul__",
    "__rmul__",
    "__mod__",
    "__divmod__",
    "__pow__",
    "__truediv__",
    "__floordiv__",
    "__matmul__",
    "__neg__",
    "__pos__",
    "__abs__",
    "__invert__",
    "__and__",
    "__or__",
    "__xor__",
    "__lshift__",
    "__rshift__",
    # reflected binary ops (right-hand operand) -- reached when the LEFT operand returns
    # NotImplemented, a callback an alternative interpreter may .unwrap() unguarded.
    "__rmod__",
    "__rdivmod__",
    "__rpow__",
    "__rtruediv__",
    "__rfloordiv__",
    "__rmatmul__",
    "__rand__",
    "__ror__",
    "__rxor__",
    "__rlshift__",
    "__rrshift__",
    # in-place ops (augmented assignment) -- a distinct set of number-protocol slots.
    "__imul__",
    "__isub__",
    "__imod__",
    "__ipow__",
    "__itruediv__",
    "__ifloordiv__",
    "__imatmul__",
    "__iand__",
    "__ior__",
    "__ixor__",
    "__ilshift__",
    "__irshift__",
    # buffer protocol (PEP 688) -- a raising __buffer__ detonates a native buffer acquisition
    # (memoryview(...), struct/array/C-level readbuffer), an error path C code often skips.
    "__buffer__",
    "__release_buffer__",
    "__enter__",
    "__exit__",
    "__get__",
    "__set__",
    "__delete__",
    "__aiter__",
    "__anext__",
    "__await__",
    "__ceil__",
    "__floor__",
)


def _make_superbomb_slot(name):
    def _slot(self, *args, **kwargs):
        counts = self._bomb_calls
        counts[name] = counts.get(name, 0) + 1
        if counts[name] > self._bomb_delay:
            raise _bomb_exc()("fusil superbomb via %s" % name)

    _slot.__name__ = name
    return _slot


class _SuperBombMeta(type):
    def __new__(mcls, cname, bases, namespace):
        for _name in _SUPERBOMB_DUNDERS:
            namespace.setdefault(_name, _make_superbomb_slot(_name))
        return super().__new__(mcls, cname, bases, namespace)


class SuperBomb(metaclass=_SuperBombMeta):
    """Every protocol dunder raises a random exception on first use or after a random delay."""

    def __init__(self, max_delay=3):
        # object.__setattr__: __setattr__ itself is not armed, but keep construction robust
        # regardless of what a subclass/metaclass does.
        object.__setattr__(self, "_bomb_calls", {})
        object.__setattr__(self, "_bomb_delay", _bomb_random.randint(0, max_delay))


# --- File-like bombs (target the common "try fd, else .read()" C pattern) ----------------


class ReadBomb(_BombBase):
    """A file-like whose read()/readline() succeed a random few times, then raise -- the
    delayed mid-parse failure that surfaces partial-read error handling."""

    def read(self, *args, **kwargs):
        self._fire()
        return b""

    def readline(self, *args, **kwargs):
        self._fire()
        return b""

    def readlines(self, *args, **kwargs):
        self._fire()
        return []

    def __iter__(self):
        return iter((b"line\n",))

    def seek(self, *args, **kwargs):
        return 0

    def tell(self):
        return 0

    def close(self):
        pass


class WrongTypeFile:
    """read() returns the wrong type (int, not bytes/str) -- targets C code that assumes the
    return of read() is a buffer."""

    def read(self, *args, **kwargs):
        return 123456

    def readline(self, *args, **kwargs):
        return 123456

    def close(self):
        pass


class FilenoBomb:
    """fileno() raises (looks like a bad/again fd) while read() keeps working -- targets the
    'try obj.fileno(), fall back to obj.read()' branch and its error handling."""

    def fileno(self):
        raise _bomb_exc()("fusil fileno bomb")

    def read(self, *args, **kwargs):
        return b""

    def readable(self):
        return True

    def close(self):
        pass


# --- Metaclass / descriptor bombs (target attribute-access C paths) ----------------------


class _HiddenNameMeta(type):
    """Metaclass whose attribute access raises for the identity names C code reads unchecked
    (``Py_TYPE(obj)->tp_name`` analogues via ``PyObject_GetAttrString(cls, "__name__")``)."""

    def __getattribute__(cls, name):
        if name in ("__name__", "__qualname__", "__module__"):
            raise _bomb_exc()("fusil hidden name: %s" % name)
        return super().__getattribute__(name)


class HiddenNameType(metaclass=_HiddenNameMeta):
    """A *class* (pass it, don't instantiate) whose __name__/__qualname__/__module__ raise."""


class _RaisingGet:
    """A data descriptor whose __get__/__set__ raise -- hits unguarded PyErr_Clear in getattr
    fallbacks when installed on a commonly-probed attribute name."""

    def __get__(self, obj, objtype=None):
        raise _bomb_exc()("fusil descriptor get")

    def __set__(self, obj, value):
        raise _bomb_exc()("fusil descriptor set")


class DescriptorBomb:
    """An instance whose class carries raising data-descriptors on attribute names C code
    commonly probes."""

    value = _RaisingGet()
    name = _RaisingGet()
    read = _RaisingGet()
    __wrapped__ = _RaisingGet()


class _StatefulHashMeta(type):
    """Metaclass hash that succeeds at first (registration) then raises after a random delay --
    targets type-keyed registries (``PyDict_GetItem`` on a class key that changes hashability)."""

    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)
        # list cell so __hash__ can mutate without triggering __setattr__ machinery
        cls._bomb_hash_state = [0, _bomb_random.randint(0, 3)]
        return cls

    def __hash__(cls):
        state = super().__getattribute__("_bomb_hash_state")
        state[0] += 1
        if state[0] > state[1]:
            raise _bomb_exc()("fusil stateful hash")
        return 0


class StatefulHashType(metaclass=_StatefulHashMeta):
    """A *class* (pass it, don't instantiate) whose hash works, then arms and starts raising."""


# --- Instance-check metaclass bombs (target isinstance()/issubclass() C paths) ------------
#
# A hostile metaclass whose __instancecheck__ / __subclasscheck__ is a landmine. Pass the CLASS
# (not an instance) where a type is expected -- isinstance(x, ThisType), issubclass(C, ThisType),
# abc registration / __subclasshook__, functools.singledispatch, or any C code that type-checks an
# argument against a user-supplied class -- and the check RAISES or LIES. C paths that call
# PyObject_IsInstance / PyObject_IsSubclass and then PyErr_Clear (or cache the result and dispatch
# on it) either skip the raised error or act on a contradictory, changing answer.


class _RaisingInstanceCheckMeta(type):
    """__instancecheck__/__subclasscheck__ succeed a random number of times, then raise."""

    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)
        # list cell so the check can mutate state without going through __setattr__
        cls._bomb_ic_state = [0, _bomb_random.randint(0, 3)]
        return cls

    def _bomb_ic_fire(cls):
        state = type.__getattribute__(cls, "_bomb_ic_state")
        state[0] += 1
        if state[0] > state[1]:
            raise _bomb_exc()("fusil instancecheck")

    def __instancecheck__(cls, instance):
        cls._bomb_ic_fire()
        return False

    def __subclasscheck__(cls, subclass):
        cls._bomb_ic_fire()
        return False


class RaisingInstanceCheckType(metaclass=_RaisingInstanceCheckMeta):
    """A *class* (pass it, don't instantiate) whose isinstance()/issubclass() work, then arm and
    raise -- detonating a C error path that type-checks a value against this passed class."""


class _LyingInstanceCheckMeta(type):
    """__instancecheck__/__subclasscheck__ SUCCEED but flip their answer every few calls, so a C
    routine that checks the same class more than once (a cached isinstance dispatch, an abc
    __subclasshook__ memo, a singledispatch registry) sees membership change underneath it."""

    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)
        cls._bomb_ic_state = [0, _bomb_random.randint(2, 4)]
        return cls

    def __instancecheck__(cls, instance):
        state = type.__getattribute__(cls, "_bomb_ic_state")
        state[0] += 1
        return (state[0] // state[1]) % 2 == 0

    __subclasscheck__ = __instancecheck__


class LyingInstanceCheckType(metaclass=_LyingInstanceCheckMeta):
    """A *class* (pass it, don't instantiate) whose isinstance()/issubclass() alternate True/False,
    so repeated checks against it contradict each other -- desyncs cached type dispatch."""


# --- Numeric / in-place-protocol bombs (target PyNumber_InPlace* and reflected ops) -------
#
# The number protocol's in-place slots (__iadd__/__imul__/... reached by ``x OP= bomb``), reflected
# slots (__radd__/... reached by ``n OP bomb`` when the left operand returns NotImplemented), and
# forward slots (__add__/...) all SUCCEED here but return a value of an UNEXPECTED type (str, None,
# bytes, a huge int, NaN, self). A C accumulator/reducer -- ``PyNumber_InPlaceAdd(acc, x)`` in a
# loop, sum() / functools.reduce, the same-type in-place fast paths (_BINARY_OP_INPLACE_ADD_UNICODE
# and friends) -- that assumes the op returns the original type then operates on the wrong-typed
# result. SuperBomb *raises* from these slots; this bomb *lies*, so it slips past a raise-guard and
# corrupts the value instead. Hash/repr are left working so it survives arg-passing to reach a slot.

_LYING_NUMERIC_RETURNS = (0, 1, -1, "", "lie", b"", None, 10**30, float("nan"))

_LYING_NUMERIC_SLOTS = (
    "__add__",
    "__radd__",
    "__iadd__",
    "__sub__",
    "__rsub__",
    "__isub__",
    "__mul__",
    "__rmul__",
    "__imul__",
    "__mod__",
    "__rmod__",
    "__imod__",
    "__pow__",
    "__rpow__",
    "__ipow__",
    "__truediv__",
    "__rtruediv__",
    "__itruediv__",
    "__floordiv__",
    "__rfloordiv__",
    "__ifloordiv__",
    "__and__",
    "__rand__",
    "__iand__",
    "__or__",
    "__ror__",
    "__ior__",
    "__xor__",
    "__rxor__",
    "__ixor__",
    "__lshift__",
    "__rlshift__",
    "__ilshift__",
    "__rshift__",
    "__rrshift__",
    "__irshift__",
    "__matmul__",
    "__rmatmul__",
    "__imatmul__",
)


def _make_lying_numeric_slot(name):
    def _slot(self, *args):
        return _bomb_random.choice(_LYING_NUMERIC_RETURNS)

    _slot.__name__ = name
    return _slot


class _LyingInplaceMeta(type):
    def __new__(mcls, cname, bases, namespace):
        for _name in _LYING_NUMERIC_SLOTS:
            namespace.setdefault(_name, _make_lying_numeric_slot(_name))
        return super().__new__(mcls, cname, bases, namespace)


class LyingInplace(metaclass=_LyingInplaceMeta):
    """Every numeric slot (forward / reflected / in-place) succeeds but returns a random UNEXPECTED
    type, so ``acc += bomb`` / ``n + bomb`` / a C reduction loop gets a str/None/huge-int/NaN where
    it expected a number and then operates on the wrong type. Hashable + reprable (left working) so
    it reaches the number-protocol slot instead of detonating during arg handling."""


# Names the argument generator instantiates (as ``Name()``); every class constructs with no
# required arguments and self-randomises its delay/exception.
BOMB_CLASS_NAMES = [
    "HashBomb",
    "EqBomb",
    "IndexBomb",
    "LenBomb",
    "LyingLen",
    "ReprBomb",
    "FailingIterator",
    "SuperBomb",
    "ReadBomb",
    "WrongTypeFile",
    "FilenoBomb",
    "DescriptorBomb",
    # Reentrant-mutation bombs: MUTATE the container mid-C-operation (reentrancy / UAF class),
    # rather than raising. Self-contained, built with no required args, arg-injectable like the rest.
    "ReentrantClearList",
    "ReentrantClearDict",
    "MutatingIterable",
    # Stateful / lying bombs: a slot SUCCEEDS but returns an inconsistent answer across calls
    # (__len__ grows, __hash__ changes while keyed, iterator flips element type mid-stream).
    "GrowingLen",
    "MutatingHash",
    "TypeFlipIterator",
    # Lying-equality bombs: hashable + storable, but __eq__ / identity lie (claim equal to a
    # value they are not, or flip the answer on each call) -- desyncs C hash tables.
    "LyingEq",
    "ShiftyEq",
    # Numeric / in-place-protocol bomb: forward/reflected/in-place ops succeed but return an
    # unexpected type, corrupting a C accumulator that assumes the op preserves the operand type.
    "LyingInplace",
]

# Names the argument generator passes *as the class object itself* (not instantiated) -- the
# bomb is the type: a metaclass turns attribute/hash access, or an isinstance()/issubclass()
# check, on the class into a landmine.
BOMB_TYPE_NAMES = [
    "HiddenNameType",
    "StatefulHashType",
    # Instance-check metaclass bombs: isinstance(x, T) / issubclass(C, T) against these raises
    # or flips its answer -- detonates / desyncs C type-check-against-a-passed-class paths.
    "RaisingInstanceCheckType",
    "LyingInstanceCheckType",
]


def errback(*args, **kw):
    raise ValueError('errback called')


class Liar1:
    def __eq__(self, other):
        return True

class Liar2:
    def __eq__(self, other):
        return False

liar1, liar2 = Liar1(), Liar2()

class Evil:
    def __eq__(self, other):
        for attr in dir(other):
            try: other.__dict__[attr] = errback
            except: pass

evil = Evil()


# Define a custom exception to distinguish our check from others.
class JITCorrectnessError(AssertionError): pass

# Helper for correctness testing that handles NaN, lambdas, and complex numbers.
import math
import types
def compare_results(a, b):
    if isinstance(a, types.FunctionType) and a.__name__ == '<lambda>' and \
       isinstance(b, types.FunctionType) and b.__name__ == '<lambda>':
        return True # Treat two lambdas as equal for our purposes
    if isinstance(a, complex) and isinstance(b, complex):
        a_real_nan = math.isnan(a.real)
        b_real_nan = math.isnan(b.real)
        a_imag_nan = math.isnan(a.imag)
        b_imag_nan = math.isnan(b.imag)
        real_match = (a.real == b.real) or (a_real_nan and b_real_nan)
        imag_match = (a.imag == b.imag) or (a_imag_nan and b_imag_nan)
        return real_match and imag_match
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    if isinstance(a, object) and isinstance(b, object):
        return True
    if isinstance(a, tuple) and isinstance(b, tuple) and len(a) == len(b):
        return all(compare_results(x, y) for x, y in zip(a, b))
    return a == b

SENTINEL_VALUE = object()

def callMethod(prefix, obj_to_call, method_name, *arguments, verbose=True):
    func_display_name = f"multiprocessing.popen_fork.{method_name}()" if obj_to_call is multiprocessing.popen_fork else f"{obj_to_call.__class__.__name__}.{method_name}()"
    message = f"[{prefix}] {func_display_name}"
    if verbose:
        print(message, file=stderr)
    result = SENTINEL_VALUE
    try:
        func_to_run = getattr(obj_to_call, method_name)
        for _ in range(int(3)):
            result = func_to_run(*arguments)
    except (Exception, SystemExit, KeyboardInterrupt) as err:
        try:
            errmsg = repr(err)
        except Exception as e_repr:
            try:
                _repr_detail = str(e_repr)
            except Exception:
                _repr_detail = '<unprintable>'
            errmsg = f'Error during repr: {e_repr.__class__.__name__}: {_repr_detail}'
        errmsg = errmsg.encode('ASCII', 'replace').decode('ASCII')
        if verbose:
            print(f"[{prefix}] {func_display_name} => EXCEPTION: {err.__class__.__name__}: {errmsg}", file=stderr)
        result = SENTINEL_VALUE
    if verbose:
        print(f"[{prefix}] -explicit garbage collection-", file=stderr)
    collect()
    if result is not SENTINEL_VALUE:
        fuzzer_threads_alive.append(Thread(target=func_to_run, args=arguments, name=message))
    return result

def callFunc(prefix, func_name_str, *arguments, verbose=True):
    return callMethod(prefix, multiprocessing.popen_fork, func_name_str, *arguments, verbose=verbose)

fuzz_target_module = multiprocessing.popen_fork

fuzzer_threads_alive = []
fuzzer_async_tasks = []


# FUSIL_BOILERPLATE_END


import sys
# Do NOT import `random` (the function) -- it shadows the `random` module that
# embedded tricky-object code imports and calls as `random.randint(...)`.
from random import choice, randint, sample
from sys import stderr, path as sys_path



print("--- Fuzzing 1 classes in multiprocessing.popen_fork ---", file=stderr)
print("[c1] Attempting to instantiate class: Popen", file=stderr)
instance_c1_popen = None # Initialize instance variable
try:
    instance_c1_popen = callFunc('c1_init', 'Popen',
        False,
      )
except Exception as e_instantiate:
    instance_c1_popen = None
    print("[c1] Failed to instantiate Popen: {e_instantiate.__class__.__name__} {e_instantiate}", file=stderr)
    instance_c1_popen = None

try:
    print(f"--- (Depth 0) Dispatching Fuzz for: {instance_c1_popen!r} (hint: Popen, prefix: c1_popen_ops) ---", file=stderr)
except Exception as e:
    print(f"--- (Depth 0) Error calling repr() prefix: c1_popen_ops) ---", file=stderr)
if instance_c1_popen is not None:
    if skip_trivial_type(instance_c1_popen):
        print(f'Skipping deep diving on instance_c1_popen {type(instance_c1_popen)}', file=stderr)
    try:
        print(f'Instance {instance_c1_popen!r} (actual type {type(instance_c1_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    except Exception as e:
        print(f'Error printing instance repr() { e } (actual type {type(instance_c1_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    if skip_trivial_type(instance_c1_popen):
        print(f'Skipping deep diving on instance_c1_popen {type(instance_c1_popen)}', file=stderr)
    else:
        print(f'Instance instance_c1_popen (type {type(instance_c1_popen).__name__}) has no specific fuzzer, doing generic calls.', file=stderr)
        c1_popen_ops_generic_methods = []
        try:
            for c1_popen_ops_generic_attr_name in dir(instance_c1_popen):
                if c1_popen_ops_generic_attr_name.startswith('_'): continue
                try:
                    c1_popen_ops_generic_attr_val = getattr(instance_c1_popen, c1_popen_ops_generic_attr_name)
                    if callable(c1_popen_ops_generic_attr_val) and c1_popen_ops_generic_attr_name not in _FUSIL_METHOD_BLACKLIST: c1_popen_ops_generic_methods.append((c1_popen_ops_generic_attr_name, c1_popen_ops_generic_attr_val))
                except Exception: pass
        except Exception: c1_popen_ops_generic_methods = [] # Failed to get methods
        if c1_popen_ops_generic_methods:
            print(f'Found {len(c1_popen_ops_generic_methods)} callable methods for generic fuzzing of instance_c1_popen', file=stderr)
            for _i_c1_popen_ops_generic in range(min(len(c1_popen_ops_generic_methods), 15)):
                c1_popen_ops_generic_method_name_to_call, c1_popen_ops_generic_method_obj_to_call = choice(c1_popen_ops_generic_methods)
                # Conceptual call to generic method fuzzer
                if c1_popen_ops_generic_method_name_to_call not in _FUSIL_METHOD_BLACKLIST: callMethod(f'c1_popen_ops_generic_gen{_i_c1_popen_ops_generic}', instance_c1_popen, c1_popen_ops_generic_method_name_to_call)

if instance_c1_popen is not None and instance_c1_popen is not SENTINEL_VALUE:
    print(f"--- Fuzzing instance: instance_c1_popen (type hint: Popen, prefix: c1m) ---", file=stderr)
    if skip_trivial_type(instance_c1_popen):
        print(f'Skipping deep diving on instance_c1_popen {type(instance_c1_popen)}', file=stderr)
    # General method fuzzing for instance_c1_popen
    try:
        res_c1m1 = callMethod("c1m1", instance_c1_popen, "poll",
            EqBomb(),
        verbose=True)
    except Exception as _argexc_c1m1:
        print("[c1m1] call skipped (argument build failed):", repr(_argexc_c1m1), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c1_popen, 'poll')
    except Exception as e_get_target_func:
        print(f"[c1m1] Failed to get attribute poll from instance_c1_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(chr(127),), name='c1m1_poll')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c1m1] Failed to create thread for poll: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c1m1_poll(target_func=target_func):
            print("Starting async task: async_call_c1m1_poll", file=stderr)
            time.sleep(0.000139) # Small delay
            try:
                target_func(Exception('fuzzer_generated_exception'))
            except Exception as e_async_call:
                print(f"[c1m1] Exception in async task async_call_c1m1_poll: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c1m1_poll", file=stderr)
        fuzzer_async_tasks.append(async_call_c1m1_poll)

    try:
        res_c1m2 = callMethod("c1m2", instance_c1_popen, "_launch",
            "?%5\x81\xFB\xE9",
        verbose=True)
    except Exception as _argexc_c1m2:
        print("[c1m2] call skipped (argument build failed):", repr(_argexc_c1m2), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c1_popen, '_launch')
    except Exception as e_get_target_func:
        print(f"[c1m2] Failed to get attribute _launch from instance_c1_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(")\xCD",), name='c1m2__launch')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c1m2] Failed to create thread for _launch: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c1m2__launch(target_func=target_func):
            print("Starting async task: async_call_c1m2__launch", file=stderr)
            time.sleep(0.000760) # Small delay
            try:
                target_func(TypeFlipIterator())
            except Exception as e_async_call:
                print(f"[c1m2] Exception in async task async_call_c1m2__launch: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c1m2__launch", file=stderr)
        fuzzer_async_tasks.append(async_call_c1m2__launch)

    try:
        res_c1m3 = callMethod("c1m3", instance_c1_popen, "__delattr__",
            weird_classes['weird_OrderedDict'],
        verbose=True)
    except Exception as _argexc_c1m3:
        print("[c1m3] call skipped (argument build failed):", repr(_argexc_c1m3), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c1_popen, '__delattr__')
    except Exception as e_get_target_func:
        print(f"[c1m3] Failed to get attribute __delattr__ from instance_c1_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(HashBomb(),), name='c1m3___delattr__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c1m3] Failed to create thread for __delattr__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c1m3___delattr__(target_func=target_func):
            print("Starting async task: async_call_c1m3___delattr__", file=stderr)
            time.sleep(0.000482) # Small delay
            try:
                target_func(tricky_staticmethod)
            except Exception as e_async_call:
                print(f"[c1m3] Exception in async task async_call_c1m3___delattr__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c1m3___delattr__", file=stderr)
        fuzzer_async_tasks.append(async_call_c1m3___delattr__)

    try:
        res_c1m4 = callMethod("c1m4", instance_c1_popen, "__setattr__",
            tricky_property,
            LenBomb(),
        verbose=True)
    except Exception as _argexc_c1m4:
        print("[c1m4] call skipped (argument build failed):", repr(_argexc_c1m4), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c1_popen, '__setattr__')
    except Exception as e_get_target_func:
        print(f"[c1m4] Failed to get attribute __setattr__ from instance_c1_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(errback, type), name='c1m4___setattr__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c1m4] Failed to create thread for __setattr__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c1m4___setattr__(target_func=target_func):
            print("Starting async task: async_call_c1m4___setattr__", file=stderr)
            time.sleep(0.000860) # Small delay
            try:
                target_func(LyingInstanceCheckType, list[weird_classes['weird_dict']])
            except Exception as e_async_call:
                print(f"[c1m4] Exception in async task async_call_c1m4___setattr__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c1m4___setattr__", file=stderr)
        fuzzer_async_tasks.append(async_call_c1m4___setattr__)

    try:
        res_c1m5 = callMethod("c1m5", instance_c1_popen, "__getstate__",
        verbose=True)
    except Exception as _argexc_c1m5:
        print("[c1m5] call skipped (argument build failed):", repr(_argexc_c1m5), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c1_popen, '__getstate__')
    except Exception as e_get_target_func:
        print(f"[c1m5] Failed to get attribute __getstate__ from instance_c1_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c1m5___getstate__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c1m5] Failed to create thread for __getstate__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c1m5___getstate__(target_func=target_func):
            print("Starting async task: async_call_c1m5___getstate__", file=stderr)
            time.sleep(0.000805) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c1m5] Exception in async task async_call_c1m5___getstate__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c1m5___getstate__", file=stderr)
        fuzzer_async_tasks.append(async_call_c1m5___getstate__)

    try:
        res_c1m6 = callMethod("c1m6", instance_c1_popen, "__dir__",
        verbose=True)
    except Exception as _argexc_c1m6:
        print("[c1m6] call skipped (argument build failed):", repr(_argexc_c1m6), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c1_popen, '__dir__')
    except Exception as e_get_target_func:
        print(f"[c1m6] Failed to get attribute __dir__ from instance_c1_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c1m6___dir__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c1m6] Failed to create thread for __dir__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c1m6___dir__(target_func=target_func):
            print("Starting async task: async_call_c1m6___dir__", file=stderr)
            time.sleep(0.000004) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c1m6] Exception in async task async_call_c1m6___dir__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c1m6___dir__", file=stderr)
        fuzzer_async_tasks.append(async_call_c1m6___dir__)

    try:
        res_c1m7 = callMethod("c1m7", instance_c1_popen, "__str__",
        verbose=True)
    except Exception as _argexc_c1m7:
        print("[c1m7] call skipped (argument build failed):", repr(_argexc_c1m7), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c1_popen, '__str__')
    except Exception as e_get_target_func:
        print(f"[c1m7] Failed to get attribute __str__ from instance_c1_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c1m7___str__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c1m7] Failed to create thread for __str__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c1m7___str__(target_func=target_func):
            print("Starting async task: async_call_c1m7___str__", file=stderr)
            time.sleep(0.000891) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c1m7] Exception in async task async_call_c1m7___str__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c1m7___str__", file=stderr)
        fuzzer_async_tasks.append(async_call_c1m7___str__)

    try:
        res_c1m8 = callMethod("c1m8", instance_c1_popen, "__gt__",
            list[weird_classes['weird_complex']] | weird_classes['weird_OrderedDict'] | big_union,
        verbose=True)
    except Exception as _argexc_c1m8:
        print("[c1m8] call skipped (argument build failed):", repr(_argexc_c1m8), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c1_popen, '__gt__')
    except Exception as e_get_target_func:
        print(f"[c1m8] Failed to get attribute __gt__ from instance_c1_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(582.631,), name='c1m8___gt__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c1m8] Failed to create thread for __gt__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c1m8___gt__(target_func=target_func):
            print("Starting async task: async_call_c1m8___gt__", file=stderr)
            time.sleep(0.000262) # Small delay
            try:
                target_func(None)
            except Exception as e_async_call:
                print(f"[c1m8] Exception in async task async_call_c1m8___gt__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c1m8___gt__", file=stderr)
        fuzzer_async_tasks.append(async_call_c1m8___gt__)

    try:
        res_c1m9 = callMethod("c1m9", instance_c1_popen, "__subclasshook__",
            memoryview(bytearray(b"abc\xe9\xff")),
        verbose=True)
    except Exception as _argexc_c1m9:
        print("[c1m9] call skipped (argument build failed):", repr(_argexc_c1m9), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c1_popen, '__subclasshook__')
    except Exception as e_get_target_func:
        print(f"[c1m9] Failed to get attribute __subclasshook__ from instance_c1_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(Exception('fuzzer_generated_exception'),), name='c1m9___subclasshook__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c1m9] Failed to create thread for __subclasshook__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c1m9___subclasshook__(target_func=target_func):
            print("Starting async task: async_call_c1m9___subclasshook__", file=stderr)
            time.sleep(0.000985) # Small delay
            try:
                target_func(list[weird_classes['weird_Counter']])
            except Exception as e_async_call:
                print(f"[c1m9] Exception in async task async_call_c1m9___subclasshook__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c1m9___subclasshook__", file=stderr)
        fuzzer_async_tasks.append(async_call_c1m9___subclasshook__)

    try:
        res_c1m10 = callMethod("c1m10", instance_c1_popen, "__str__",
        verbose=True)
    except Exception as _argexc_c1m10:
        print("[c1m10] call skipped (argument build failed):", repr(_argexc_c1m10), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c1_popen, '__str__')
    except Exception as e_get_target_func:
        print(f"[c1m10] Failed to get attribute __str__ from instance_c1_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c1m10___str__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c1m10] Failed to create thread for __str__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c1m10___str__(target_func=target_func):
            print("Starting async task: async_call_c1m10___str__", file=stderr)
            time.sleep(0.000599) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c1m10] Exception in async task async_call_c1m10___str__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c1m10___str__", file=stderr)
        fuzzer_async_tasks.append(async_call_c1m10___str__)

    try:
        res_c1m11 = callMethod("c1m11", instance_c1_popen, "__ge__",
        verbose=True)
    except Exception as _argexc_c1m11:
        print("[c1m11] call skipped (argument build failed):", repr(_argexc_c1m11), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c1_popen, '__ge__')
    except Exception as e_get_target_func:
        print(f"[c1m11] Failed to get attribute __ge__ from instance_c1_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c1m11___ge__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c1m11] Failed to create thread for __ge__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c1m11___ge__(target_func=target_func):
            print("Starting async task: async_call_c1m11___ge__", file=stderr)
            time.sleep(0.000677) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c1m11] Exception in async task async_call_c1m11___ge__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c1m11___ge__", file=stderr)
        fuzzer_async_tasks.append(async_call_c1m11___ge__)

    try:
        res_c1m12 = callMethod("c1m12", instance_c1_popen, "__repr__",
        verbose=True)
    except Exception as _argexc_c1m12:
        print("[c1m12] call skipped (argument build failed):", repr(_argexc_c1m12), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c1_popen, '__repr__')
    except Exception as e_get_target_func:
        print(f"[c1m12] Failed to get attribute __repr__ from instance_c1_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c1m12___repr__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c1m12] Failed to create thread for __repr__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c1m12___repr__(target_func=target_func):
            print("Starting async task: async_call_c1m12___repr__", file=stderr)
            time.sleep(0.000139) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c1m12] Exception in async task async_call_c1m12___repr__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c1m12___repr__", file=stderr)
        fuzzer_async_tasks.append(async_call_c1m12___repr__)

    try:
        res_c1m13 = callMethod("c1m13", instance_c1_popen, "__init_subclass__",
            "\xB6\xE8n\"=6",
        verbose=True)
    except Exception as _argexc_c1m13:
        print("[c1m13] call skipped (argument build failed):", repr(_argexc_c1m13), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c1_popen, '__init_subclass__')
    except Exception as e_get_target_func:
        print(f"[c1m13] Failed to get attribute __init_subclass__ from instance_c1_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(errback,), name='c1m13___init_subclass__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c1m13] Failed to create thread for __init_subclass__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c1m13___init_subclass__(target_func=target_func):
            print("Starting async task: async_call_c1m13___init_subclass__", file=stderr)
            time.sleep(0.000938) # Small delay
            try:
                target_func(1j)
            except Exception as e_async_call:
                print(f"[c1m13] Exception in async task async_call_c1m13___init_subclass__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c1m13___init_subclass__", file=stderr)
        fuzzer_async_tasks.append(async_call_c1m13___init_subclass__)

    try:
        res_c1m14 = callMethod("c1m14", instance_c1_popen, "__reduce_ex__",
            MagicMock(),
        verbose=True)
    except Exception as _argexc_c1m14:
        print("[c1m14] call skipped (argument build failed):", repr(_argexc_c1m14), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c1_popen, '__reduce_ex__')
    except Exception as e_get_target_func:
        print(f"[c1m14] Failed to get attribute __reduce_ex__ from instance_c1_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(errback,), name='c1m14___reduce_ex__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c1m14] Failed to create thread for __reduce_ex__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c1m14___reduce_ex__(target_func=target_func):
            print("Starting async task: async_call_c1m14___reduce_ex__", file=stderr)
            time.sleep(0.000579) # Small delay
            try:
                target_func(errback)
            except Exception as e_async_call:
                print(f"[c1m14] Exception in async task async_call_c1m14___reduce_ex__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c1m14___reduce_ex__", file=stderr)
        fuzzer_async_tasks.append(async_call_c1m14___reduce_ex__)

    try:
        res_c1m15 = callMethod("c1m15", instance_c1_popen, "terminate",
        verbose=True)
    except Exception as _argexc_c1m15:
        print("[c1m15] call skipped (argument build failed):", repr(_argexc_c1m15), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c1_popen, 'terminate')
    except Exception as e_get_target_func:
        print(f"[c1m15] Failed to get attribute terminate from instance_c1_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c1m15_terminate')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c1m15] Failed to create thread for terminate: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c1m15_terminate(target_func=target_func):
            print("Starting async task: async_call_c1m15_terminate", file=stderr)
            time.sleep(0.000696) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c1m15] Exception in async task async_call_c1m15_terminate: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c1m15_terminate", file=stderr)
        fuzzer_async_tasks.append(async_call_c1m15_terminate)

    print(f"--- Finished fuzzing instance: instance_c1_popen ---", file=stderr)

    del instance_c1_popen # Cleanup instance
    print("[c1] -explicit garbage collection for class instance-", file=stderr)
    collect()

print("[c2] Attempting to instantiate class: Popen", file=stderr)
instance_c2_popen = None # Initialize instance variable
try:
    instance_c2_popen = callFunc('c2_init', 'Popen',
        MutatingIterable(),
      )
except Exception as e_instantiate:
    instance_c2_popen = None
    print("[c2] Failed to instantiate Popen: {e_instantiate.__class__.__name__} {e_instantiate}", file=stderr)
    instance_c2_popen = None

try:
    print(f"--- (Depth 0) Dispatching Fuzz for: {instance_c2_popen!r} (hint: Popen, prefix: c2_popen_ops) ---", file=stderr)
except Exception as e:
    print(f"--- (Depth 0) Error calling repr() prefix: c2_popen_ops) ---", file=stderr)
if instance_c2_popen is not None:
    if skip_trivial_type(instance_c2_popen):
        print(f'Skipping deep diving on instance_c2_popen {type(instance_c2_popen)}', file=stderr)
    try:
        print(f'Instance {instance_c2_popen!r} (actual type {type(instance_c2_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    except Exception as e:
        print(f'Error printing instance repr() { e } (actual type {type(instance_c2_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    if skip_trivial_type(instance_c2_popen):
        print(f'Skipping deep diving on instance_c2_popen {type(instance_c2_popen)}', file=stderr)
    else:
        print(f'Instance instance_c2_popen (type {type(instance_c2_popen).__name__}) has no specific fuzzer, doing generic calls.', file=stderr)
        c2_popen_ops_generic_methods = []
        try:
            for c2_popen_ops_generic_attr_name in dir(instance_c2_popen):
                if c2_popen_ops_generic_attr_name.startswith('_'): continue
                try:
                    c2_popen_ops_generic_attr_val = getattr(instance_c2_popen, c2_popen_ops_generic_attr_name)
                    if callable(c2_popen_ops_generic_attr_val) and c2_popen_ops_generic_attr_name not in _FUSIL_METHOD_BLACKLIST: c2_popen_ops_generic_methods.append((c2_popen_ops_generic_attr_name, c2_popen_ops_generic_attr_val))
                except Exception: pass
        except Exception: c2_popen_ops_generic_methods = [] # Failed to get methods
        if c2_popen_ops_generic_methods:
            print(f'Found {len(c2_popen_ops_generic_methods)} callable methods for generic fuzzing of instance_c2_popen', file=stderr)
            for _i_c2_popen_ops_generic in range(min(len(c2_popen_ops_generic_methods), 15)):
                c2_popen_ops_generic_method_name_to_call, c2_popen_ops_generic_method_obj_to_call = choice(c2_popen_ops_generic_methods)
                # Conceptual call to generic method fuzzer
                if c2_popen_ops_generic_method_name_to_call not in _FUSIL_METHOD_BLACKLIST: callMethod(f'c2_popen_ops_generic_gen{_i_c2_popen_ops_generic}', instance_c2_popen, c2_popen_ops_generic_method_name_to_call)

if instance_c2_popen is not None and instance_c2_popen is not SENTINEL_VALUE:
    print(f"--- Fuzzing instance: instance_c2_popen (type hint: Popen, prefix: c2m) ---", file=stderr)
    if skip_trivial_type(instance_c2_popen):
        print(f'Skipping deep diving on instance_c2_popen {type(instance_c2_popen)}', file=stderr)
    # General method fuzzing for instance_c2_popen
    try:
        res_c2m1 = callMethod("c2m1", instance_c2_popen, "__reduce__",
        verbose=True)
    except Exception as _argexc_c2m1:
        print("[c2m1] call skipped (argument build failed):", repr(_argexc_c2m1), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c2_popen, '__reduce__')
    except Exception as e_get_target_func:
        print(f"[c2m1] Failed to get attribute __reduce__ from instance_c2_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c2m1___reduce__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c2m1] Failed to create thread for __reduce__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c2m1___reduce__(target_func=target_func):
            print("Starting async task: async_call_c2m1___reduce__", file=stderr)
            time.sleep(0.000737) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c2m1] Exception in async task async_call_c2m1___reduce__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c2m1___reduce__", file=stderr)
        fuzzer_async_tasks.append(async_call_c2m1___reduce__)

    try:
        res_c2m2 = callMethod("c2m2", instance_c2_popen, "kill",
            "\'\xB2\x00",
        verbose=True)
    except Exception as _argexc_c2m2:
        print("[c2m2] call skipped (argument build failed):", repr(_argexc_c2m2), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c2_popen, 'kill')
    except Exception as e_get_target_func:
        print(f"[c2m2] Failed to get attribute kill from instance_c2_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(dict[weird_classes['weird_bytes']],), name='c2m2_kill')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c2m2] Failed to create thread for kill: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c2m2_kill(target_func=target_func):
            print("Starting async task: async_call_c2m2_kill", file=stderr)
            time.sleep(0.000861) # Small delay
            try:
                target_func(memoryview(b"abc\xe9\xff"))
            except Exception as e_async_call:
                print(f"[c2m2] Exception in async task async_call_c2m2_kill: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c2m2_kill", file=stderr)
        fuzzer_async_tasks.append(async_call_c2m2_kill)

    try:
        res_c2m3 = callMethod("c2m3", instance_c2_popen, "duplicate_for_child",
            tricky_list_with_cycle,
        verbose=True)
    except Exception as _argexc_c2m3:
        print("[c2m3] call skipped (argument build failed):", repr(_argexc_c2m3), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c2_popen, 'duplicate_for_child')
    except Exception as e_get_target_func:
        print(f"[c2m3] Failed to get attribute duplicate_for_child from instance_c2_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(SuperBomb(),), name='c2m3_duplicate_for_child')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c2m3] Failed to create thread for duplicate_for_child: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c2m3_duplicate_for_child(target_func=target_func):
            print("Starting async task: async_call_c2m3_duplicate_for_child", file=stderr)
            time.sleep(0.000213) # Small delay
            try:
                target_func(ReprBomb())
            except Exception as e_async_call:
                print(f"[c2m3] Exception in async task async_call_c2m3_duplicate_for_child: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c2m3_duplicate_for_child", file=stderr)
        fuzzer_async_tasks.append(async_call_c2m3_duplicate_for_child)

    try:
        res_c2m4 = callMethod("c2m4", instance_c2_popen, "__str__",
        verbose=True)
    except Exception as _argexc_c2m4:
        print("[c2m4] call skipped (argument build failed):", repr(_argexc_c2m4), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c2_popen, '__str__')
    except Exception as e_get_target_func:
        print(f"[c2m4] Failed to get attribute __str__ from instance_c2_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c2m4___str__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c2m4] Failed to create thread for __str__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c2m4___str__(target_func=target_func):
            print("Starting async task: async_call_c2m4___str__", file=stderr)
            time.sleep(0.000003) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c2m4] Exception in async task async_call_c2m4___str__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c2m4___str__", file=stderr)
        fuzzer_async_tasks.append(async_call_c2m4___str__)

    try:
        res_c2m5 = callMethod("c2m5", instance_c2_popen, "__hash__",
        verbose=True)
    except Exception as _argexc_c2m5:
        print("[c2m5] call skipped (argument build failed):", repr(_argexc_c2m5), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c2_popen, '__hash__')
    except Exception as e_get_target_func:
        print(f"[c2m5] Failed to get attribute __hash__ from instance_c2_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c2m5___hash__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c2m5] Failed to create thread for __hash__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c2m5___hash__(target_func=target_func):
            print("Starting async task: async_call_c2m5___hash__", file=stderr)
            time.sleep(0.000825) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c2m5] Exception in async task async_call_c2m5___hash__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c2m5___hash__", file=stderr)
        fuzzer_async_tasks.append(async_call_c2m5___hash__)

    try:
        res_c2m6 = callMethod("c2m6", instance_c2_popen, "__init_subclass__",
            Exception('fuzzer_generated_exception'),
        verbose=True)
    except Exception as _argexc_c2m6:
        print("[c2m6] call skipped (argument build failed):", repr(_argexc_c2m6), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c2_popen, '__init_subclass__')
    except Exception as e_get_target_func:
        print(f"[c2m6] Failed to get attribute __init_subclass__ from instance_c2_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(86.15,), name='c2m6___init_subclass__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c2m6] Failed to create thread for __init_subclass__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c2m6___init_subclass__(target_func=target_func):
            print("Starting async task: async_call_c2m6___init_subclass__", file=stderr)
            time.sleep(0.000043) # Small delay
            try:
                target_func('/tmp/fusil-fixtures/fusil_fixture.bin')
            except Exception as e_async_call:
                print(f"[c2m6] Exception in async task async_call_c2m6___init_subclass__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c2m6___init_subclass__", file=stderr)
        fuzzer_async_tasks.append(async_call_c2m6___init_subclass__)

    try:
        res_c2m7 = callMethod("c2m7", instance_c2_popen, "__init__",
            weird_classes['weird_deque'],
        verbose=True)
    except Exception as _argexc_c2m7:
        print("[c2m7] call skipped (argument build failed):", repr(_argexc_c2m7), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c2_popen, '__init__')
    except Exception as e_get_target_func:
        print(f"[c2m7] Failed to get attribute __init__ from instance_c2_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(IndexBomb(),), name='c2m7___init__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c2m7] Failed to create thread for __init__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c2m7___init__(target_func=target_func):
            print("Starting async task: async_call_c2m7___init__", file=stderr)
            time.sleep(0.000888) # Small delay
            try:
                target_func(IndexBomb())
            except Exception as e_async_call:
                print(f"[c2m7] Exception in async task async_call_c2m7___init__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c2m7___init__", file=stderr)
        fuzzer_async_tasks.append(async_call_c2m7___init__)

    try:
        res_c2m8 = callMethod("c2m8", instance_c2_popen, "__lt__",
            Liar2,
        verbose=True)
    except Exception as _argexc_c2m8:
        print("[c2m8] call skipped (argument build failed):", repr(_argexc_c2m8), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c2_popen, '__lt__')
    except Exception as e_get_target_func:
        print(f"[c2m8] Failed to get attribute __lt__ from instance_c2_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(Evil(),), name='c2m8___lt__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c2m8] Failed to create thread for __lt__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c2m8___lt__(target_func=target_func):
            print("Starting async task: async_call_c2m8___lt__", file=stderr)
            time.sleep(0.000452) # Small delay
            try:
                target_func(MutatingHash())
            except Exception as e_async_call:
                print(f"[c2m8] Exception in async task async_call_c2m8___lt__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c2m8___lt__", file=stderr)
        fuzzer_async_tasks.append(async_call_c2m8___lt__)

    try:
        res_c2m9 = callMethod("c2m9", instance_c2_popen, "__new__",
            HashBomb(),
            weird_instances['weird_str_special'],
            '/tmp/fusil-fixtures/fusil_fixture.txt',
        verbose=True)
    except Exception as _argexc_c2m9:
        print("[c2m9] call skipped (argument build failed):", repr(_argexc_c2m9), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c2_popen, '__new__')
    except Exception as e_get_target_func:
        print(f"[c2m9] Failed to get attribute __new__ from instance_c2_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("\u0C6C\uE0FB\u18F1\u5B07\u73F2\u1B4A\u3C19\uC5E0\u1BD3\u4286\uFAA6\u5562\uA457\u715D\u77F0\u2913\uD0E5\u3929\u9C6A", MutatingIterable(), "\u5E6F\u057E\uE69B\u3D58\u2306\u4F26\u888E"), name='c2m9___new__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c2m9] Failed to create thread for __new__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c2m9___new__(target_func=target_func):
            print("Starting async task: async_call_c2m9___new__", file=stderr)
            time.sleep(0.000628) # Small delay
            try:
                target_func(LyingInstanceCheckType, FailingIterator(), "\uF4B8\u5CBA\u97D6\u58EE\u2CA9\u2FCE\u05E2\u95A0\u56A2\u466B\uCDA7\u9A83\u22F7")
            except Exception as e_async_call:
                print(f"[c2m9] Exception in async task async_call_c2m9___new__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c2m9___new__", file=stderr)
        fuzzer_async_tasks.append(async_call_c2m9___new__)

    try:
        res_c2m10 = callMethod("c2m10", instance_c2_popen, "__reduce__",
            MutatingIterable(),
        verbose=True)
    except Exception as _argexc_c2m10:
        print("[c2m10] call skipped (argument build failed):", repr(_argexc_c2m10), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c2_popen, '__reduce__')
    except Exception as e_get_target_func:
        print(f"[c2m10] Failed to get attribute __reduce__ from instance_c2_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(sys.maxsize + 1,), name='c2m10___reduce__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c2m10] Failed to create thread for __reduce__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c2m10___reduce__(target_func=target_func):
            print("Starting async task: async_call_c2m10___reduce__", file=stderr)
            time.sleep(0.000045) # Small delay
            try:
                target_func(MutatingIterable())
            except Exception as e_async_call:
                print(f"[c2m10] Exception in async task async_call_c2m10___reduce__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c2m10___reduce__", file=stderr)
        fuzzer_async_tasks.append(async_call_c2m10___reduce__)

    try:
        res_c2m11 = callMethod("c2m11", instance_c2_popen, "__ne__",
            weird_instances['weird_int_2**31-1'],
        verbose=True)
    except Exception as _argexc_c2m11:
        print("[c2m11] call skipped (argument build failed):", repr(_argexc_c2m11), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c2_popen, '__ne__')
    except Exception as e_get_target_func:
        print(f"[c2m11] Failed to get attribute __ne__ from instance_c2_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(r"BvMY\wz.yV*\WgvU\S\b\d.?pjxBbW..hJOLl",), name='c2m11___ne__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c2m11] Failed to create thread for __ne__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c2m11___ne__(target_func=target_func):
            print("Starting async task: async_call_c2m11___ne__", file=stderr)
            time.sleep(0.000352) # Small delay
            try:
                target_func(r"smH.*ptiO\wlR?.tUmGCE\ZrmQzmBw\Z.\W.UlXap")
            except Exception as e_async_call:
                print(f"[c2m11] Exception in async task async_call_c2m11___ne__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c2m11___ne__", file=stderr)
        fuzzer_async_tasks.append(async_call_c2m11___ne__)

    try:
        res_c2m12 = callMethod("c2m12", instance_c2_popen, "__reduce__",
        verbose=True)
    except Exception as _argexc_c2m12:
        print("[c2m12] call skipped (argument build failed):", repr(_argexc_c2m12), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c2_popen, '__reduce__')
    except Exception as e_get_target_func:
        print(f"[c2m12] Failed to get attribute __reduce__ from instance_c2_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c2m12___reduce__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c2m12] Failed to create thread for __reduce__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c2m12___reduce__(target_func=target_func):
            print("Starting async task: async_call_c2m12___reduce__", file=stderr)
            time.sleep(0.000718) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c2m12] Exception in async task async_call_c2m12___reduce__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c2m12___reduce__", file=stderr)
        fuzzer_async_tasks.append(async_call_c2m12___reduce__)

    try:
        res_c2m13 = callMethod("c2m13", instance_c2_popen, "_launch",
            HashBomb(),
        verbose=True)
    except Exception as _argexc_c2m13:
        print("[c2m13] call skipped (argument build failed):", repr(_argexc_c2m13), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c2_popen, '_launch')
    except Exception as e_get_target_func:
        print(f"[c2m13] Failed to get attribute _launch from instance_c2_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(tuple[weird_classes['weird_frozenset']],), name='c2m13__launch')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c2m13] Failed to create thread for _launch: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c2m13__launch(target_func=target_func):
            print("Starting async task: async_call_c2m13__launch", file=stderr)
            time.sleep(0.000128) # Small delay
            try:
                target_func("./././z3/30ZgeiftjrNGhLc1/..")
            except Exception as e_async_call:
                print(f"[c2m13] Exception in async task async_call_c2m13__launch: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c2m13__launch", file=stderr)
        fuzzer_async_tasks.append(async_call_c2m13__launch)

    try:
        res_c2m14 = callMethod("c2m14", instance_c2_popen, "__reduce__",
        verbose=True)
    except Exception as _argexc_c2m14:
        print("[c2m14] call skipped (argument build failed):", repr(_argexc_c2m14), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c2_popen, '__reduce__')
    except Exception as e_get_target_func:
        print(f"[c2m14] Failed to get attribute __reduce__ from instance_c2_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c2m14___reduce__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c2m14] Failed to create thread for __reduce__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c2m14___reduce__(target_func=target_func):
            print("Starting async task: async_call_c2m14___reduce__", file=stderr)
            time.sleep(0.000698) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c2m14] Exception in async task async_call_c2m14___reduce__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c2m14___reduce__", file=stderr)
        fuzzer_async_tasks.append(async_call_c2m14___reduce__)

    try:
        res_c2m15 = callMethod("c2m15", instance_c2_popen, "terminate",
        verbose=True)
    except Exception as _argexc_c2m15:
        print("[c2m15] call skipped (argument build failed):", repr(_argexc_c2m15), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c2_popen, 'terminate')
    except Exception as e_get_target_func:
        print(f"[c2m15] Failed to get attribute terminate from instance_c2_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c2m15_terminate')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c2m15] Failed to create thread for terminate: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c2m15_terminate(target_func=target_func):
            print("Starting async task: async_call_c2m15_terminate", file=stderr)
            time.sleep(0.000779) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c2m15] Exception in async task async_call_c2m15_terminate: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c2m15_terminate", file=stderr)
        fuzzer_async_tasks.append(async_call_c2m15_terminate)

    print(f"--- Finished fuzzing instance: instance_c2_popen ---", file=stderr)

    del instance_c2_popen # Cleanup instance
    print("[c2] -explicit garbage collection for class instance-", file=stderr)
    collect()

print("[c3] Attempting to instantiate class: Popen", file=stderr)
instance_c3_popen = None # Initialize instance variable
try:
    instance_c3_popen = callFunc('c3_init', 'Popen',
        -1j,
      )
except Exception as e_instantiate:
    instance_c3_popen = None
    print("[c3] Failed to instantiate Popen: {e_instantiate.__class__.__name__} {e_instantiate}", file=stderr)
    instance_c3_popen = None

try:
    print(f"--- (Depth 0) Dispatching Fuzz for: {instance_c3_popen!r} (hint: Popen, prefix: c3_popen_ops) ---", file=stderr)
except Exception as e:
    print(f"--- (Depth 0) Error calling repr() prefix: c3_popen_ops) ---", file=stderr)
if instance_c3_popen is not None:
    if skip_trivial_type(instance_c3_popen):
        print(f'Skipping deep diving on instance_c3_popen {type(instance_c3_popen)}', file=stderr)
    try:
        print(f'Instance {instance_c3_popen!r} (actual type {type(instance_c3_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    except Exception as e:
        print(f'Error printing instance repr() { e } (actual type {type(instance_c3_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    if skip_trivial_type(instance_c3_popen):
        print(f'Skipping deep diving on instance_c3_popen {type(instance_c3_popen)}', file=stderr)
    else:
        print(f'Instance instance_c3_popen (type {type(instance_c3_popen).__name__}) has no specific fuzzer, doing generic calls.', file=stderr)
        c3_popen_ops_generic_methods = []
        try:
            for c3_popen_ops_generic_attr_name in dir(instance_c3_popen):
                if c3_popen_ops_generic_attr_name.startswith('_'): continue
                try:
                    c3_popen_ops_generic_attr_val = getattr(instance_c3_popen, c3_popen_ops_generic_attr_name)
                    if callable(c3_popen_ops_generic_attr_val) and c3_popen_ops_generic_attr_name not in _FUSIL_METHOD_BLACKLIST: c3_popen_ops_generic_methods.append((c3_popen_ops_generic_attr_name, c3_popen_ops_generic_attr_val))
                except Exception: pass
        except Exception: c3_popen_ops_generic_methods = [] # Failed to get methods
        if c3_popen_ops_generic_methods:
            print(f'Found {len(c3_popen_ops_generic_methods)} callable methods for generic fuzzing of instance_c3_popen', file=stderr)
            for _i_c3_popen_ops_generic in range(min(len(c3_popen_ops_generic_methods), 15)):
                c3_popen_ops_generic_method_name_to_call, c3_popen_ops_generic_method_obj_to_call = choice(c3_popen_ops_generic_methods)
                # Conceptual call to generic method fuzzer
                if c3_popen_ops_generic_method_name_to_call not in _FUSIL_METHOD_BLACKLIST: callMethod(f'c3_popen_ops_generic_gen{_i_c3_popen_ops_generic}', instance_c3_popen, c3_popen_ops_generic_method_name_to_call)

if instance_c3_popen is not None and instance_c3_popen is not SENTINEL_VALUE:
    print(f"--- Fuzzing instance: instance_c3_popen (type hint: Popen, prefix: c3m) ---", file=stderr)
    if skip_trivial_type(instance_c3_popen):
        print(f'Skipping deep diving on instance_c3_popen {type(instance_c3_popen)}', file=stderr)
    # General method fuzzing for instance_c3_popen
    try:
        res_c3m1 = callMethod("c3m1", instance_c3_popen, "__ne__",
            r"^(?:a|aa)*$",
        verbose=True)
    except Exception as _argexc_c3m1:
        print("[c3m1] call skipped (argument build failed):", repr(_argexc_c3m1), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c3_popen, '__ne__')
    except Exception as e_get_target_func:
        print(f"[c3m1] Failed to get attribute __ne__ from instance_c3_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(StatefulHashType,), name='c3m1___ne__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c3m1] Failed to create thread for __ne__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c3m1___ne__(target_func=target_func):
            print("Starting async task: async_call_c3m1___ne__", file=stderr)
            time.sleep(0.000792) # Small delay
            try:
                target_func(list[weird_classes['weird_OrderedDict']] | weird_classes['weird_bytearray'] | big_union)
            except Exception as e_async_call:
                print(f"[c3m1] Exception in async task async_call_c3m1___ne__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c3m1___ne__", file=stderr)
        fuzzer_async_tasks.append(async_call_c3m1___ne__)

    try:
        res_c3m2 = callMethod("c3m2", instance_c3_popen, "__reduce_ex__",
            list[weird_classes['weird_bytes']] | weird_classes['weird_list'] | big_union,
        verbose=True)
    except Exception as _argexc_c3m2:
        print("[c3m2] call skipped (argument build failed):", repr(_argexc_c3m2), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c3_popen, '__reduce_ex__')
    except Exception as e_get_target_func:
        print(f"[c3m2] Failed to get attribute __reduce_ex__ from instance_c3_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("\xEA\xBF\x18(\x8E",), name='c3m2___reduce_ex__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c3m2] Failed to create thread for __reduce_ex__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c3m2___reduce_ex__(target_func=target_func):
            print("Starting async task: async_call_c3m2___reduce_ex__", file=stderr)
            time.sleep(0.000845) # Small delay
            try:
                target_func(False)
            except Exception as e_async_call:
                print(f"[c3m2] Exception in async task async_call_c3m2___reduce_ex__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c3m2___reduce_ex__", file=stderr)
        fuzzer_async_tasks.append(async_call_c3m2___reduce_ex__)

    try:
        res_c3m3 = callMethod("c3m3", instance_c3_popen, "__init__",
            list[weird_classes['weird_int']],
        verbose=True)
    except Exception as _argexc_c3m3:
        print("[c3m3] call skipped (argument build failed):", repr(_argexc_c3m3), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c3_popen, '__init__')
    except Exception as e_get_target_func:
        print(f"[c3m3] Failed to get attribute __init__ from instance_c3_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(Exception('fuzzer_generated_exception'),), name='c3m3___init__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c3m3] Failed to create thread for __init__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c3m3___init__(target_func=target_func):
            print("Starting async task: async_call_c3m3___init__", file=stderr)
            time.sleep(0.000079) # Small delay
            try:
                target_func(-2.699)
            except Exception as e_async_call:
                print(f"[c3m3] Exception in async task async_call_c3m3___init__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c3m3___init__", file=stderr)
        fuzzer_async_tasks.append(async_call_c3m3___init__)

    try:
        res_c3m4 = callMethod("c3m4", instance_c3_popen, "__gt__",
            weird_instances['weird_complex_neg_sys_maxsize'],
        verbose=True)
    except Exception as _argexc_c3m4:
        print("[c3m4] call skipped (argument build failed):", repr(_argexc_c3m4), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c3_popen, '__gt__')
    except Exception as e_get_target_func:
        print(f"[c3m4] Failed to get attribute __gt__ from instance_c3_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(EqBomb(),), name='c3m4___gt__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c3m4] Failed to create thread for __gt__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c3m4___gt__(target_func=target_func):
            print("Starting async task: async_call_c3m4___gt__", file=stderr)
            time.sleep(0.000024) # Small delay
            try:
                target_func(tricky_classmethod_descriptor)
            except Exception as e_async_call:
                print(f"[c3m4] Exception in async task async_call_c3m4___gt__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c3m4___gt__", file=stderr)
        fuzzer_async_tasks.append(async_call_c3m4___gt__)

    try:
        res_c3m5 = callMethod("c3m5", instance_c3_popen, "__lt__",
            2,
        verbose=True)
    except Exception as _argexc_c3m5:
        print("[c3m5] call skipped (argument build failed):", repr(_argexc_c3m5), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c3_popen, '__lt__')
    except Exception as e_get_target_func:
        print(f"[c3m5] Failed to get attribute __lt__ from instance_c3_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(sys.maxsize - 1,), name='c3m5___lt__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c3m5] Failed to create thread for __lt__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c3m5___lt__(target_func=target_func):
            print("Starting async task: async_call_c3m5___lt__", file=stderr)
            time.sleep(0.000056) # Small delay
            try:
                target_func(DescriptorBomb())
            except Exception as e_async_call:
                print(f"[c3m5] Exception in async task async_call_c3m5___lt__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c3m5___lt__", file=stderr)
        fuzzer_async_tasks.append(async_call_c3m5___lt__)

    try:
        res_c3m6 = callMethod("c3m6", instance_c3_popen, "__hash__",
        verbose=True)
    except Exception as _argexc_c3m6:
        print("[c3m6] call skipped (argument build failed):", repr(_argexc_c3m6), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c3_popen, '__hash__')
    except Exception as e_get_target_func:
        print(f"[c3m6] Failed to get attribute __hash__ from instance_c3_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c3m6___hash__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c3m6] Failed to create thread for __hash__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c3m6___hash__(target_func=target_func):
            print("Starting async task: async_call_c3m6___hash__", file=stderr)
            time.sleep(0.000947) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c3m6] Exception in async task async_call_c3m6___hash__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c3m6___hash__", file=stderr)
        fuzzer_async_tasks.append(async_call_c3m6___hash__)

    try:
        res_c3m7 = callMethod("c3m7", instance_c3_popen, "__repr__",
        verbose=True)
    except Exception as _argexc_c3m7:
        print("[c3m7] call skipped (argument build failed):", repr(_argexc_c3m7), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c3_popen, '__repr__')
    except Exception as e_get_target_func:
        print(f"[c3m7] Failed to get attribute __repr__ from instance_c3_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c3m7___repr__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c3m7] Failed to create thread for __repr__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c3m7___repr__(target_func=target_func):
            print("Starting async task: async_call_c3m7___repr__", file=stderr)
            time.sleep(0.000772) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c3m7] Exception in async task async_call_c3m7___repr__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c3m7___repr__", file=stderr)
        fuzzer_async_tasks.append(async_call_c3m7___repr__)

    try:
        res_c3m8 = callMethod("c3m8", instance_c3_popen, "__init_subclass__",
            Liar1,
        verbose=True)
    except Exception as _argexc_c3m8:
        print("[c3m8] call skipped (argument build failed):", repr(_argexc_c3m8), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c3_popen, '__init_subclass__')
    except Exception as e_get_target_func:
        print(f"[c3m8] Failed to get attribute __init_subclass__ from instance_c3_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(weird_instances['weird_Decimal_sys_maxsize_plus_one'],), name='c3m8___init_subclass__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c3m8] Failed to create thread for __init_subclass__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c3m8___init_subclass__(target_func=target_func):
            print("Starting async task: async_call_c3m8___init_subclass__", file=stderr)
            time.sleep(0.000354) # Small delay
            try:
                target_func(None)
            except Exception as e_async_call:
                print(f"[c3m8] Exception in async task async_call_c3m8___init_subclass__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c3m8___init_subclass__", file=stderr)
        fuzzer_async_tasks.append(async_call_c3m8___init_subclass__)

    try:
        res_c3m9 = callMethod("c3m9", instance_c3_popen, "poll",
            lambda: None,
        verbose=True)
    except Exception as _argexc_c3m9:
        print("[c3m9] call skipped (argument build failed):", repr(_argexc_c3m9), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c3_popen, 'poll')
    except Exception as e_get_target_func:
        print(f"[c3m9] Failed to get attribute poll from instance_c3_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(LyingLen(),), name='c3m9_poll')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c3m9] Failed to create thread for poll: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c3m9_poll(target_func=target_func):
            print("Starting async task: async_call_c3m9_poll", file=stderr)
            time.sleep(0.000504) # Small delay
            try:
                target_func(ReprBomb())
            except Exception as e_async_call:
                print(f"[c3m9] Exception in async task async_call_c3m9_poll: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c3m9_poll", file=stderr)
        fuzzer_async_tasks.append(async_call_c3m9_poll)

    try:
        res_c3m10 = callMethod("c3m10", instance_c3_popen, "__reduce__",
        verbose=True)
    except Exception as _argexc_c3m10:
        print("[c3m10] call skipped (argument build failed):", repr(_argexc_c3m10), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c3_popen, '__reduce__')
    except Exception as e_get_target_func:
        print(f"[c3m10] Failed to get attribute __reduce__ from instance_c3_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c3m10___reduce__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c3m10] Failed to create thread for __reduce__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c3m10___reduce__(target_func=target_func):
            print("Starting async task: async_call_c3m10___reduce__", file=stderr)
            time.sleep(0.000845) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c3m10] Exception in async task async_call_c3m10___reduce__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c3m10___reduce__", file=stderr)
        fuzzer_async_tasks.append(async_call_c3m10___reduce__)

    try:
        res_c3m11 = callMethod("c3m11", instance_c3_popen, "__ne__",
            -3.2587,
        verbose=True)
    except Exception as _argexc_c3m11:
        print("[c3m11] call skipped (argument build failed):", repr(_argexc_c3m11), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c3_popen, '__ne__')
    except Exception as e_get_target_func:
        print(f"[c3m11] Failed to get attribute __ne__ from instance_c3_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("fllXk_gzqXiKDi/e1/hGXZA./jc7-cZc",), name='c3m11___ne__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c3m11] Failed to create thread for __ne__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c3m11___ne__(target_func=target_func):
            print("Starting async task: async_call_c3m11___ne__", file=stderr)
            time.sleep(0.000393) # Small delay
            try:
                target_func(961.5043)
            except Exception as e_async_call:
                print(f"[c3m11] Exception in async task async_call_c3m11___ne__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c3m11___ne__", file=stderr)
        fuzzer_async_tasks.append(async_call_c3m11___ne__)

    try:
        res_c3m12 = callMethod("c3m12", instance_c3_popen, "duplicate_for_child",
            WrongTypeFile(),
        verbose=True)
    except Exception as _argexc_c3m12:
        print("[c3m12] call skipped (argument build failed):", repr(_argexc_c3m12), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c3_popen, 'duplicate_for_child')
    except Exception as e_get_target_func:
        print(f"[c3m12] Failed to get attribute duplicate_for_child from instance_c3_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(77.2079,), name='c3m12_duplicate_for_child')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c3m12] Failed to create thread for duplicate_for_child: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c3m12_duplicate_for_child(target_func=target_func):
            print("Starting async task: async_call_c3m12_duplicate_for_child", file=stderr)
            time.sleep(0.000522) # Small delay
            try:
                target_func(False)
            except Exception as e_async_call:
                print(f"[c3m12] Exception in async task async_call_c3m12_duplicate_for_child: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c3m12_duplicate_for_child", file=stderr)
        fuzzer_async_tasks.append(async_call_c3m12_duplicate_for_child)

    try:
        res_c3m13 = callMethod("c3m13", instance_c3_popen, "__ne__",
            "\u3E59\u1280\u4EBF\uF1D2\u8875\u4B13\uB365\uEAB0\u4E4C\uEBD3\uB515",
        verbose=True)
    except Exception as _argexc_c3m13:
        print("[c3m13] call skipped (argument build failed):", repr(_argexc_c3m13), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c3_popen, '__ne__')
    except Exception as e_get_target_func:
        print(f"[c3m13] Failed to get attribute __ne__ from instance_c3_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(weird_classes['weird_object'],), name='c3m13___ne__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c3m13] Failed to create thread for __ne__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c3m13___ne__(target_func=target_func):
            print("Starting async task: async_call_c3m13___ne__", file=stderr)
            time.sleep(0.000825) # Small delay
            try:
                target_func(LyingLen())
            except Exception as e_async_call:
                print(f"[c3m13] Exception in async task async_call_c3m13___ne__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c3m13___ne__", file=stderr)
        fuzzer_async_tasks.append(async_call_c3m13___ne__)

    try:
        res_c3m14 = callMethod("c3m14", instance_c3_popen, "__eq__",
            bytearray(b"abc\xe9\xff"),
        verbose=True)
    except Exception as _argexc_c3m14:
        print("[c3m14] call skipped (argument build failed):", repr(_argexc_c3m14), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c3_popen, '__eq__')
    except Exception as e_get_target_func:
        print(f"[c3m14] Failed to get attribute __eq__ from instance_c3_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(22.45,), name='c3m14___eq__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c3m14] Failed to create thread for __eq__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c3m14___eq__(target_func=target_func):
            print("Starting async task: async_call_c3m14___eq__", file=stderr)
            time.sleep(0.000332) # Small delay
            try:
                target_func("eFul9220xfAiXOp9iH3eBk/_Sj0/mp/tJFlM2aIIjrgPK/r4fkXuLOz.Wh5BDVjzU//K")
            except Exception as e_async_call:
                print(f"[c3m14] Exception in async task async_call_c3m14___eq__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c3m14___eq__", file=stderr)
        fuzzer_async_tasks.append(async_call_c3m14___eq__)

    try:
        res_c3m15 = callMethod("c3m15", instance_c3_popen, "__repr__",
            "\x16",
        verbose=True)
    except Exception as _argexc_c3m15:
        print("[c3m15] call skipped (argument build failed):", repr(_argexc_c3m15), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c3_popen, '__repr__')
    except Exception as e_get_target_func:
        print(f"[c3m15] Failed to get attribute __repr__ from instance_c3_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(weird_classes['weird_frozenset'],), name='c3m15___repr__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c3m15] Failed to create thread for __repr__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c3m15___repr__(target_func=target_func):
            print("Starting async task: async_call_c3m15___repr__", file=stderr)
            time.sleep(0.000717) # Small delay
            try:
                target_func(RaisingInstanceCheckType)
            except Exception as e_async_call:
                print(f"[c3m15] Exception in async task async_call_c3m15___repr__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c3m15___repr__", file=stderr)
        fuzzer_async_tasks.append(async_call_c3m15___repr__)

    print(f"--- Finished fuzzing instance: instance_c3_popen ---", file=stderr)

    del instance_c3_popen # Cleanup instance
    print("[c3] -explicit garbage collection for class instance-", file=stderr)
    collect()

print("[c4] Attempting to instantiate class: Popen", file=stderr)
instance_c4_popen = None # Initialize instance variable
try:
    instance_c4_popen = callFunc('c4_init', 'Popen',
        ReentrantClearList(),
      )
except Exception as e_instantiate:
    instance_c4_popen = None
    print("[c4] Failed to instantiate Popen: {e_instantiate.__class__.__name__} {e_instantiate}", file=stderr)
    instance_c4_popen = None

try:
    print(f"--- (Depth 0) Dispatching Fuzz for: {instance_c4_popen!r} (hint: Popen, prefix: c4_popen_ops) ---", file=stderr)
except Exception as e:
    print(f"--- (Depth 0) Error calling repr() prefix: c4_popen_ops) ---", file=stderr)
if instance_c4_popen is not None:
    if skip_trivial_type(instance_c4_popen):
        print(f'Skipping deep diving on instance_c4_popen {type(instance_c4_popen)}', file=stderr)
    try:
        print(f'Instance {instance_c4_popen!r} (actual type {type(instance_c4_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    except Exception as e:
        print(f'Error printing instance repr() { e } (actual type {type(instance_c4_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    if skip_trivial_type(instance_c4_popen):
        print(f'Skipping deep diving on instance_c4_popen {type(instance_c4_popen)}', file=stderr)
    else:
        print(f'Instance instance_c4_popen (type {type(instance_c4_popen).__name__}) has no specific fuzzer, doing generic calls.', file=stderr)
        c4_popen_ops_generic_methods = []
        try:
            for c4_popen_ops_generic_attr_name in dir(instance_c4_popen):
                if c4_popen_ops_generic_attr_name.startswith('_'): continue
                try:
                    c4_popen_ops_generic_attr_val = getattr(instance_c4_popen, c4_popen_ops_generic_attr_name)
                    if callable(c4_popen_ops_generic_attr_val) and c4_popen_ops_generic_attr_name not in _FUSIL_METHOD_BLACKLIST: c4_popen_ops_generic_methods.append((c4_popen_ops_generic_attr_name, c4_popen_ops_generic_attr_val))
                except Exception: pass
        except Exception: c4_popen_ops_generic_methods = [] # Failed to get methods
        if c4_popen_ops_generic_methods:
            print(f'Found {len(c4_popen_ops_generic_methods)} callable methods for generic fuzzing of instance_c4_popen', file=stderr)
            for _i_c4_popen_ops_generic in range(min(len(c4_popen_ops_generic_methods), 15)):
                c4_popen_ops_generic_method_name_to_call, c4_popen_ops_generic_method_obj_to_call = choice(c4_popen_ops_generic_methods)
                # Conceptual call to generic method fuzzer
                if c4_popen_ops_generic_method_name_to_call not in _FUSIL_METHOD_BLACKLIST: callMethod(f'c4_popen_ops_generic_gen{_i_c4_popen_ops_generic}', instance_c4_popen, c4_popen_ops_generic_method_name_to_call)

if instance_c4_popen is not None and instance_c4_popen is not SENTINEL_VALUE:
    print(f"--- Fuzzing instance: instance_c4_popen (type hint: Popen, prefix: c4m) ---", file=stderr)
    if skip_trivial_type(instance_c4_popen):
        print(f'Skipping deep diving on instance_c4_popen {type(instance_c4_popen)}', file=stderr)
    # General method fuzzing for instance_c4_popen
    try:
        res_c4m1 = callMethod("c4m1", instance_c4_popen, "__setattr__",
            IndexBomb(),
            454.7063,
        verbose=True)
    except Exception as _argexc_c4m1:
        print("[c4m1] call skipped (argument build failed):", repr(_argexc_c4m1), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c4_popen, '__setattr__')
    except Exception as e_get_target_func:
        print(f"[c4m1] Failed to get attribute __setattr__ from instance_c4_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(EqBomb(), tuple[weird_classes['weird_list']]), name='c4m1___setattr__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c4m1] Failed to create thread for __setattr__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c4m1___setattr__(target_func=target_func):
            print("Starting async task: async_call_c4m1___setattr__", file=stderr)
            time.sleep(0.000730) # Small delay
            try:
                target_func(Liar1, "\xBA\xA0\x07\x1F\xD8\xF7\xA6\xD2")
            except Exception as e_async_call:
                print(f"[c4m1] Exception in async task async_call_c4m1___setattr__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c4m1___setattr__", file=stderr)
        fuzzer_async_tasks.append(async_call_c4m1___setattr__)

    try:
        res_c4m2 = callMethod("c4m2", instance_c4_popen, "__init_subclass__",
            8,
        verbose=True)
    except Exception as _argexc_c4m2:
        print("[c4m2] call skipped (argument build failed):", repr(_argexc_c4m2), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c4_popen, '__init_subclass__')
    except Exception as e_get_target_func:
        print(f"[c4m2] Failed to get attribute __init_subclass__ from instance_c4_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(EqBomb(),), name='c4m2___init_subclass__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c4m2] Failed to create thread for __init_subclass__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c4m2___init_subclass__(target_func=target_func):
            print("Starting async task: async_call_c4m2___init_subclass__", file=stderr)
            time.sleep(0.000060) # Small delay
            try:
                target_func("bB75sjcy.8L-HF03h2i.4/PBAQsQsmS4cjbgu5rbaPEz0vVAR/./kc/wNOnH/iyg/q")
            except Exception as e_async_call:
                print(f"[c4m2] Exception in async task async_call_c4m2___init_subclass__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c4m2___init_subclass__", file=stderr)
        fuzzer_async_tasks.append(async_call_c4m2___init_subclass__)

    try:
        res_c4m3 = callMethod("c4m3", instance_c4_popen, "__ge__",
            "\uD4C9\uE380\u25DE\u6AC1\u1676\u5F21\uAF7D\uB39C\u2A21\uC8F2\uC2CD\u98F4\u7362\u3038\uB9CA\uE5B9\u0F78\u1E59\u686F\uAE80",
        verbose=True)
    except Exception as _argexc_c4m3:
        print("[c4m3] call skipped (argument build failed):", repr(_argexc_c4m3), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c4_popen, '__ge__')
    except Exception as e_get_target_func:
        print(f"[c4m3] Failed to get attribute __ge__ from instance_c4_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(WrongTypeFile(),), name='c4m3___ge__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c4m3] Failed to create thread for __ge__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c4m3___ge__(target_func=target_func):
            print("Starting async task: async_call_c4m3___ge__", file=stderr)
            time.sleep(0.000431) # Small delay
            try:
                target_func(tricky_dict)
            except Exception as e_async_call:
                print(f"[c4m3] Exception in async task async_call_c4m3___ge__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c4m3___ge__", file=stderr)
        fuzzer_async_tasks.append(async_call_c4m3___ge__)

    try:
        res_c4m4 = callMethod("c4m4", instance_c4_popen, "__eq__",
            EqBomb(),
        verbose=True)
    except Exception as _argexc_c4m4:
        print("[c4m4] call skipped (argument build failed):", repr(_argexc_c4m4), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c4_popen, '__eq__')
    except Exception as e_get_target_func:
        print(f"[c4m4] Failed to get attribute __eq__ from instance_c4_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(memoryview(bytearray(b"abc\xe9\xff")),), name='c4m4___eq__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c4m4] Failed to create thread for __eq__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c4m4___eq__(target_func=target_func):
            print("Starting async task: async_call_c4m4___eq__", file=stderr)
            time.sleep(0.000833) # Small delay
            try:
                target_func(3)
            except Exception as e_async_call:
                print(f"[c4m4] Exception in async task async_call_c4m4___eq__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c4m4___eq__", file=stderr)
        fuzzer_async_tasks.append(async_call_c4m4___eq__)

    try:
        res_c4m5 = callMethod("c4m5", instance_c4_popen, "__subclasshook__",
            -18,
        verbose=True)
    except Exception as _argexc_c4m5:
        print("[c4m5] call skipped (argument build failed):", repr(_argexc_c4m5), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c4_popen, '__subclasshook__')
    except Exception as e_get_target_func:
        print(f"[c4m5] Failed to get attribute __subclasshook__ from instance_c4_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(r"No\Zn+\DCfYSN\bh..SZ.V\ZX.l\As",), name='c4m5___subclasshook__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c4m5] Failed to create thread for __subclasshook__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c4m5___subclasshook__(target_func=target_func):
            print("Starting async task: async_call_c4m5___subclasshook__", file=stderr)
            time.sleep(0.000729) # Small delay
            try:
                target_func("\U0010FFFF")
            except Exception as e_async_call:
                print(f"[c4m5] Exception in async task async_call_c4m5___subclasshook__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c4m5___subclasshook__", file=stderr)
        fuzzer_async_tasks.append(async_call_c4m5___subclasshook__)

    try:
        res_c4m6 = callMethod("c4m6", instance_c4_popen, "__lt__",
            liar1,
        verbose=True)
    except Exception as _argexc_c4m6:
        print("[c4m6] call skipped (argument build failed):", repr(_argexc_c4m6), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c4_popen, '__lt__')
    except Exception as e_get_target_func:
        print(f"[c4m6] Failed to get attribute __lt__ from instance_c4_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(r"\DHSM.kp\bsd\s\ZZ\bEU\BhQ\B.xVsm?.c?W\SwgsmmH.di",), name='c4m6___lt__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c4m6] Failed to create thread for __lt__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c4m6___lt__(target_func=target_func):
            print("Starting async task: async_call_c4m6___lt__", file=stderr)
            time.sleep(0.000764) # Small delay
            try:
                target_func("\u4FC4\u224B\uD68F\uEB9E\uF314\u3410\u7C51\u342D\u16E6\u2D91\u96DB\uEC54")
            except Exception as e_async_call:
                print(f"[c4m6] Exception in async task async_call_c4m6___lt__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c4m6___lt__", file=stderr)
        fuzzer_async_tasks.append(async_call_c4m6___lt__)

    try:
        res_c4m7 = callMethod("c4m7", instance_c4_popen, "__repr__",
        verbose=True)
    except Exception as _argexc_c4m7:
        print("[c4m7] call skipped (argument build failed):", repr(_argexc_c4m7), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c4_popen, '__repr__')
    except Exception as e_get_target_func:
        print(f"[c4m7] Failed to get attribute __repr__ from instance_c4_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c4m7___repr__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c4m7] Failed to create thread for __repr__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c4m7___repr__(target_func=target_func):
            print("Starting async task: async_call_c4m7___repr__", file=stderr)
            time.sleep(0.000449) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c4m7] Exception in async task async_call_c4m7___repr__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c4m7___repr__", file=stderr)
        fuzzer_async_tasks.append(async_call_c4m7___repr__)

    try:
        res_c4m8 = callMethod("c4m8", instance_c4_popen, "__repr__",
        verbose=True)
    except Exception as _argexc_c4m8:
        print("[c4m8] call skipped (argument build failed):", repr(_argexc_c4m8), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c4_popen, '__repr__')
    except Exception as e_get_target_func:
        print(f"[c4m8] Failed to get attribute __repr__ from instance_c4_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c4m8___repr__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c4m8] Failed to create thread for __repr__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c4m8___repr__(target_func=target_func):
            print("Starting async task: async_call_c4m8___repr__", file=stderr)
            time.sleep(0.000234) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c4m8] Exception in async task async_call_c4m8___repr__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c4m8___repr__", file=stderr)
        fuzzer_async_tasks.append(async_call_c4m8___repr__)

    try:
        res_c4m9 = callMethod("c4m9", instance_c4_popen, "__reduce__",
        verbose=True)
    except Exception as _argexc_c4m9:
        print("[c4m9] call skipped (argument build failed):", repr(_argexc_c4m9), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c4_popen, '__reduce__')
    except Exception as e_get_target_func:
        print(f"[c4m9] Failed to get attribute __reduce__ from instance_c4_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c4m9___reduce__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c4m9] Failed to create thread for __reduce__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c4m9___reduce__(target_func=target_func):
            print("Starting async task: async_call_c4m9___reduce__", file=stderr)
            time.sleep(0.000613) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c4m9] Exception in async task async_call_c4m9___reduce__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c4m9___reduce__", file=stderr)
        fuzzer_async_tasks.append(async_call_c4m9___reduce__)

    try:
        res_c4m10 = callMethod("c4m10", instance_c4_popen, "__str__",
        verbose=True)
    except Exception as _argexc_c4m10:
        print("[c4m10] call skipped (argument build failed):", repr(_argexc_c4m10), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c4_popen, '__str__')
    except Exception as e_get_target_func:
        print(f"[c4m10] Failed to get attribute __str__ from instance_c4_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c4m10___str__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c4m10] Failed to create thread for __str__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c4m10___str__(target_func=target_func):
            print("Starting async task: async_call_c4m10___str__", file=stderr)
            time.sleep(0.000414) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c4m10] Exception in async task async_call_c4m10___str__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c4m10___str__", file=stderr)
        fuzzer_async_tasks.append(async_call_c4m10___str__)

    try:
        res_c4m11 = callMethod("c4m11", instance_c4_popen, "kill",
        verbose=True)
    except Exception as _argexc_c4m11:
        print("[c4m11] call skipped (argument build failed):", repr(_argexc_c4m11), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c4_popen, 'kill')
    except Exception as e_get_target_func:
        print(f"[c4m11] Failed to get attribute kill from instance_c4_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c4m11_kill')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c4m11] Failed to create thread for kill: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c4m11_kill(target_func=target_func):
            print("Starting async task: async_call_c4m11_kill", file=stderr)
            time.sleep(0.000341) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c4m11] Exception in async task async_call_c4m11_kill: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c4m11_kill", file=stderr)
        fuzzer_async_tasks.append(async_call_c4m11_kill)

    try:
        res_c4m12 = callMethod("c4m12", instance_c4_popen, "close",
        verbose=True)
    except Exception as _argexc_c4m12:
        print("[c4m12] call skipped (argument build failed):", repr(_argexc_c4m12), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c4_popen, 'close')
    except Exception as e_get_target_func:
        print(f"[c4m12] Failed to get attribute close from instance_c4_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c4m12_close')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c4m12] Failed to create thread for close: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c4m12_close(target_func=target_func):
            print("Starting async task: async_call_c4m12_close", file=stderr)
            time.sleep(0.000987) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c4m12] Exception in async task async_call_c4m12_close: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c4m12_close", file=stderr)
        fuzzer_async_tasks.append(async_call_c4m12_close)

    try:
        res_c4m13 = callMethod("c4m13", instance_c4_popen, "__init__",
            FilenoBomb(),
        verbose=True)
    except Exception as _argexc_c4m13:
        print("[c4m13] call skipped (argument build failed):", repr(_argexc_c4m13), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c4_popen, '__init__')
    except Exception as e_get_target_func:
        print(f"[c4m13] Failed to get attribute __init__ from instance_c4_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("t1\x9FM}w",), name='c4m13___init__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c4m13] Failed to create thread for __init__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c4m13___init__(target_func=target_func):
            print("Starting async task: async_call_c4m13___init__", file=stderr)
            time.sleep(0.000849) # Small delay
            try:
                target_func(LyingLen())
            except Exception as e_async_call:
                print(f"[c4m13] Exception in async task async_call_c4m13___init__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c4m13___init__", file=stderr)
        fuzzer_async_tasks.append(async_call_c4m13___init__)

    try:
        res_c4m14 = callMethod("c4m14", instance_c4_popen, "duplicate_for_child",
            FilenoBomb(),
        verbose=True)
    except Exception as _argexc_c4m14:
        print("[c4m14] call skipped (argument build failed):", repr(_argexc_c4m14), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c4_popen, 'duplicate_for_child')
    except Exception as e_get_target_func:
        print(f"[c4m14] Failed to get attribute duplicate_for_child from instance_c4_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(IndexBomb(),), name='c4m14_duplicate_for_child')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c4m14] Failed to create thread for duplicate_for_child: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c4m14_duplicate_for_child(target_func=target_func):
            print("Starting async task: async_call_c4m14_duplicate_for_child", file=stderr)
            time.sleep(0.000094) # Small delay
            try:
                target_func('/tmp/fusil-fixtures/fusil_fixture.bin')
            except Exception as e_async_call:
                print(f"[c4m14] Exception in async task async_call_c4m14_duplicate_for_child: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c4m14_duplicate_for_child", file=stderr)
        fuzzer_async_tasks.append(async_call_c4m14_duplicate_for_child)

    try:
        res_c4m15 = callMethod("c4m15", instance_c4_popen, "__subclasshook__",
            TypeFlipIterator(),
        verbose=True)
    except Exception as _argexc_c4m15:
        print("[c4m15] call skipped (argument build failed):", repr(_argexc_c4m15), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c4_popen, '__subclasshook__')
    except Exception as e_get_target_func:
        print(f"[c4m15] Failed to get attribute __subclasshook__ from instance_c4_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(GrowingLen(),), name='c4m15___subclasshook__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c4m15] Failed to create thread for __subclasshook__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c4m15___subclasshook__(target_func=target_func):
            print("Starting async task: async_call_c4m15___subclasshook__", file=stderr)
            time.sleep(0.000762) # Small delay
            try:
                target_func(HashBomb())
            except Exception as e_async_call:
                print(f"[c4m15] Exception in async task async_call_c4m15___subclasshook__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c4m15___subclasshook__", file=stderr)
        fuzzer_async_tasks.append(async_call_c4m15___subclasshook__)

    print(f"--- Finished fuzzing instance: instance_c4_popen ---", file=stderr)

    del instance_c4_popen # Cleanup instance
    print("[c4] -explicit garbage collection for class instance-", file=stderr)
    collect()

print("[c5] Attempting to instantiate class: Popen", file=stderr)
instance_c5_popen = None # Initialize instance variable
try:
    instance_c5_popen = callFunc('c5_init', 'Popen',
        weird_classes['weird_OrderedDict'],
      )
except Exception as e_instantiate:
    instance_c5_popen = None
    print("[c5] Failed to instantiate Popen: {e_instantiate.__class__.__name__} {e_instantiate}", file=stderr)
    instance_c5_popen = None

try:
    print(f"--- (Depth 0) Dispatching Fuzz for: {instance_c5_popen!r} (hint: Popen, prefix: c5_popen_ops) ---", file=stderr)
except Exception as e:
    print(f"--- (Depth 0) Error calling repr() prefix: c5_popen_ops) ---", file=stderr)
if instance_c5_popen is not None:
    if skip_trivial_type(instance_c5_popen):
        print(f'Skipping deep diving on instance_c5_popen {type(instance_c5_popen)}', file=stderr)
    try:
        print(f'Instance {instance_c5_popen!r} (actual type {type(instance_c5_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    except Exception as e:
        print(f'Error printing instance repr() { e } (actual type {type(instance_c5_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    if skip_trivial_type(instance_c5_popen):
        print(f'Skipping deep diving on instance_c5_popen {type(instance_c5_popen)}', file=stderr)
    else:
        print(f'Instance instance_c5_popen (type {type(instance_c5_popen).__name__}) has no specific fuzzer, doing generic calls.', file=stderr)
        c5_popen_ops_generic_methods = []
        try:
            for c5_popen_ops_generic_attr_name in dir(instance_c5_popen):
                if c5_popen_ops_generic_attr_name.startswith('_'): continue
                try:
                    c5_popen_ops_generic_attr_val = getattr(instance_c5_popen, c5_popen_ops_generic_attr_name)
                    if callable(c5_popen_ops_generic_attr_val) and c5_popen_ops_generic_attr_name not in _FUSIL_METHOD_BLACKLIST: c5_popen_ops_generic_methods.append((c5_popen_ops_generic_attr_name, c5_popen_ops_generic_attr_val))
                except Exception: pass
        except Exception: c5_popen_ops_generic_methods = [] # Failed to get methods
        if c5_popen_ops_generic_methods:
            print(f'Found {len(c5_popen_ops_generic_methods)} callable methods for generic fuzzing of instance_c5_popen', file=stderr)
            for _i_c5_popen_ops_generic in range(min(len(c5_popen_ops_generic_methods), 15)):
                c5_popen_ops_generic_method_name_to_call, c5_popen_ops_generic_method_obj_to_call = choice(c5_popen_ops_generic_methods)
                # Conceptual call to generic method fuzzer
                if c5_popen_ops_generic_method_name_to_call not in _FUSIL_METHOD_BLACKLIST: callMethod(f'c5_popen_ops_generic_gen{_i_c5_popen_ops_generic}', instance_c5_popen, c5_popen_ops_generic_method_name_to_call)

if instance_c5_popen is not None and instance_c5_popen is not SENTINEL_VALUE:
    print(f"--- Fuzzing instance: instance_c5_popen (type hint: Popen, prefix: c5m) ---", file=stderr)
    if skip_trivial_type(instance_c5_popen):
        print(f'Skipping deep diving on instance_c5_popen {type(instance_c5_popen)}', file=stderr)
    # General method fuzzing for instance_c5_popen
    try:
        res_c5m1 = callMethod("c5m1", instance_c5_popen, "__getstate__",
        verbose=True)
    except Exception as _argexc_c5m1:
        print("[c5m1] call skipped (argument build failed):", repr(_argexc_c5m1), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c5_popen, '__getstate__')
    except Exception as e_get_target_func:
        print(f"[c5m1] Failed to get attribute __getstate__ from instance_c5_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c5m1___getstate__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c5m1] Failed to create thread for __getstate__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c5m1___getstate__(target_func=target_func):
            print("Starting async task: async_call_c5m1___getstate__", file=stderr)
            time.sleep(0.000593) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c5m1] Exception in async task async_call_c5m1___getstate__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c5m1___getstate__", file=stderr)
        fuzzer_async_tasks.append(async_call_c5m1___getstate__)

    try:
        res_c5m2 = callMethod("c5m2", instance_c5_popen, "__init_subclass__",
            "/IO3L1zr31-.CP5h8pXHz9C/iT6MBqFnoY_EzS9z/./",
        verbose=True)
    except Exception as _argexc_c5m2:
        print("[c5m2] call skipped (argument build failed):", repr(_argexc_c5m2), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c5_popen, '__init_subclass__')
    except Exception as e_get_target_func:
        print(f"[c5m2] Failed to get attribute __init_subclass__ from instance_c5_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(-8059,), name='c5m2___init_subclass__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c5m2] Failed to create thread for __init_subclass__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c5m2___init_subclass__(target_func=target_func):
            print("Starting async task: async_call_c5m2___init_subclass__", file=stderr)
            time.sleep(0.000416) # Small delay
            try:
                target_func(10 ** 100)
            except Exception as e_async_call:
                print(f"[c5m2] Exception in async task async_call_c5m2___init_subclass__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c5m2___init_subclass__", file=stderr)
        fuzzer_async_tasks.append(async_call_c5m2___init_subclass__)

    try:
        res_c5m3 = callMethod("c5m3", instance_c5_popen, "_launch",
        verbose=True)
    except Exception as _argexc_c5m3:
        print("[c5m3] call skipped (argument build failed):", repr(_argexc_c5m3), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c5_popen, '_launch')
    except Exception as e_get_target_func:
        print(f"[c5m3] Failed to get attribute _launch from instance_c5_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c5m3__launch')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c5m3] Failed to create thread for _launch: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c5m3__launch(target_func=target_func):
            print("Starting async task: async_call_c5m3__launch", file=stderr)
            time.sleep(0.000724) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c5m3] Exception in async task async_call_c5m3__launch: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c5m3__launch", file=stderr)
        fuzzer_async_tasks.append(async_call_c5m3__launch)

    try:
        res_c5m4 = callMethod("c5m4", instance_c5_popen, "__setattr__",
            '/tmp/fusil-fixtures/fusil_fixture.bin',
            ReentrantClearDict(),
        verbose=True)
    except Exception as _argexc_c5m4:
        print("[c5m4] call skipped (argument build failed):", repr(_argexc_c5m4), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c5_popen, '__setattr__')
    except Exception as e_get_target_func:
        print(f"[c5m4] Failed to get attribute __setattr__ from instance_c5_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(tricky_traceback, errback), name='c5m4___setattr__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c5m4] Failed to create thread for __setattr__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c5m4___setattr__(target_func=target_func):
            print("Starting async task: async_call_c5m4___setattr__", file=stderr)
            time.sleep(0.000474) # Small delay
            try:
                target_func(weird_classes['weird_tuple'], LyingEq())
            except Exception as e_async_call:
                print(f"[c5m4] Exception in async task async_call_c5m4___setattr__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c5m4___setattr__", file=stderr)
        fuzzer_async_tasks.append(async_call_c5m4___setattr__)

    try:
        res_c5m5 = callMethod("c5m5", instance_c5_popen, "__le__",
            errback,
        verbose=True)
    except Exception as _argexc_c5m5:
        print("[c5m5] call skipped (argument build failed):", repr(_argexc_c5m5), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c5_popen, '__le__')
    except Exception as e_get_target_func:
        print(f"[c5m5] Failed to get attribute __le__ from instance_c5_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(r"aD\B\dpoPz",), name='c5m5___le__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c5m5] Failed to create thread for __le__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c5m5___le__(target_func=target_func):
            print("Starting async task: async_call_c5m5___le__", file=stderr)
            time.sleep(0.000900) # Small delay
            try:
                target_func("ZC\xB3\x07\x82\x03\x8CF\x95\xD4[D \x9D&F\xEB\x7F")
            except Exception as e_async_call:
                print(f"[c5m5] Exception in async task async_call_c5m5___le__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c5m5___le__", file=stderr)
        fuzzer_async_tasks.append(async_call_c5m5___le__)

    try:
        res_c5m6 = callMethod("c5m6", instance_c5_popen, "__getstate__",
        verbose=True)
    except Exception as _argexc_c5m6:
        print("[c5m6] call skipped (argument build failed):", repr(_argexc_c5m6), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c5_popen, '__getstate__')
    except Exception as e_get_target_func:
        print(f"[c5m6] Failed to get attribute __getstate__ from instance_c5_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c5m6___getstate__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c5m6] Failed to create thread for __getstate__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c5m6___getstate__(target_func=target_func):
            print("Starting async task: async_call_c5m6___getstate__", file=stderr)
            time.sleep(0.000458) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c5m6] Exception in async task async_call_c5m6___getstate__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c5m6___getstate__", file=stderr)
        fuzzer_async_tasks.append(async_call_c5m6___getstate__)

    try:
        res_c5m7 = callMethod("c5m7", instance_c5_popen, "__dir__",
            -1.2480,
        verbose=True)
    except Exception as _argexc_c5m7:
        print("[c5m7] call skipped (argument build failed):", repr(_argexc_c5m7), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c5_popen, '__dir__')
    except Exception as e_get_target_func:
        print(f"[c5m7] Failed to get attribute __dir__ from instance_c5_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(IndexBomb(),), name='c5m7___dir__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c5m7] Failed to create thread for __dir__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c5m7___dir__(target_func=target_func):
            print("Starting async task: async_call_c5m7___dir__", file=stderr)
            time.sleep(0.000884) # Small delay
            try:
                target_func(dict[weird_classes['weird_int']] | weird_classes['weird_dict'] | big_union)
            except Exception as e_async_call:
                print(f"[c5m7] Exception in async task async_call_c5m7___dir__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c5m7___dir__", file=stderr)
        fuzzer_async_tasks.append(async_call_c5m7___dir__)

    try:
        res_c5m8 = callMethod("c5m8", instance_c5_popen, "__hash__",
        verbose=True)
    except Exception as _argexc_c5m8:
        print("[c5m8] call skipped (argument build failed):", repr(_argexc_c5m8), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c5_popen, '__hash__')
    except Exception as e_get_target_func:
        print(f"[c5m8] Failed to get attribute __hash__ from instance_c5_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c5m8___hash__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c5m8] Failed to create thread for __hash__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c5m8___hash__(target_func=target_func):
            print("Starting async task: async_call_c5m8___hash__", file=stderr)
            time.sleep(0.000371) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c5m8] Exception in async task async_call_c5m8___hash__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c5m8___hash__", file=stderr)
        fuzzer_async_tasks.append(async_call_c5m8___hash__)

    try:
        res_c5m9 = callMethod("c5m9", instance_c5_popen, "__subclasshook__",
            dict[weird_classes['weird_object']],
        verbose=True)
    except Exception as _argexc_c5m9:
        print("[c5m9] call skipped (argument build failed):", repr(_argexc_c5m9), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c5_popen, '__subclasshook__')
    except Exception as e_get_target_func:
        print(f"[c5m9] Failed to get attribute __subclasshook__ from instance_c5_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(b"\x7D\x4A\xA3\x5D\xC2\x3E\xC5\xE0\x66\xC0\x6A\xE3\x52\x92\x20\x86\x1D\xD3",), name='c5m9___subclasshook__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c5m9] Failed to create thread for __subclasshook__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c5m9___subclasshook__(target_func=target_func):
            print("Starting async task: async_call_c5m9___subclasshook__", file=stderr)
            time.sleep(0.000676) # Small delay
            try:
                target_func(True)
            except Exception as e_async_call:
                print(f"[c5m9] Exception in async task async_call_c5m9___subclasshook__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c5m9___subclasshook__", file=stderr)
        fuzzer_async_tasks.append(async_call_c5m9___subclasshook__)

    try:
        res_c5m10 = callMethod("c5m10", instance_c5_popen, "__reduce_ex__",
        verbose=True)
    except Exception as _argexc_c5m10:
        print("[c5m10] call skipped (argument build failed):", repr(_argexc_c5m10), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c5_popen, '__reduce_ex__')
    except Exception as e_get_target_func:
        print(f"[c5m10] Failed to get attribute __reduce_ex__ from instance_c5_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c5m10___reduce_ex__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c5m10] Failed to create thread for __reduce_ex__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c5m10___reduce_ex__(target_func=target_func):
            print("Starting async task: async_call_c5m10___reduce_ex__", file=stderr)
            time.sleep(0.000523) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c5m10] Exception in async task async_call_c5m10___reduce_ex__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c5m10___reduce_ex__", file=stderr)
        fuzzer_async_tasks.append(async_call_c5m10___reduce_ex__)

    try:
        res_c5m11 = callMethod("c5m11", instance_c5_popen, "__hash__",
        verbose=True)
    except Exception as _argexc_c5m11:
        print("[c5m11] call skipped (argument build failed):", repr(_argexc_c5m11), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c5_popen, '__hash__')
    except Exception as e_get_target_func:
        print(f"[c5m11] Failed to get attribute __hash__ from instance_c5_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c5m11___hash__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c5m11] Failed to create thread for __hash__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c5m11___hash__(target_func=target_func):
            print("Starting async task: async_call_c5m11___hash__", file=stderr)
            time.sleep(0.000887) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c5m11] Exception in async task async_call_c5m11___hash__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c5m11___hash__", file=stderr)
        fuzzer_async_tasks.append(async_call_c5m11___hash__)

    try:
        res_c5m12 = callMethod("c5m12", instance_c5_popen, "close",
        verbose=True)
    except Exception as _argexc_c5m12:
        print("[c5m12] call skipped (argument build failed):", repr(_argexc_c5m12), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c5_popen, 'close')
    except Exception as e_get_target_func:
        print(f"[c5m12] Failed to get attribute close from instance_c5_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c5m12_close')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c5m12] Failed to create thread for close: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c5m12_close(target_func=target_func):
            print("Starting async task: async_call_c5m12_close", file=stderr)
            time.sleep(0.000514) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c5m12] Exception in async task async_call_c5m12_close: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c5m12_close", file=stderr)
        fuzzer_async_tasks.append(async_call_c5m12_close)

    try:
        res_c5m13 = callMethod("c5m13", instance_c5_popen, "__reduce_ex__",
            "\U0010FFFF",
        verbose=True)
    except Exception as _argexc_c5m13:
        print("[c5m13] call skipped (argument build failed):", repr(_argexc_c5m13), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c5_popen, '__reduce_ex__')
    except Exception as e_get_target_func:
        print(f"[c5m13] Failed to get attribute __reduce_ex__ from instance_c5_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(RaisingInstanceCheckType,), name='c5m13___reduce_ex__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c5m13] Failed to create thread for __reduce_ex__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c5m13___reduce_ex__(target_func=target_func):
            print("Starting async task: async_call_c5m13___reduce_ex__", file=stderr)
            time.sleep(0.000472) # Small delay
            try:
                target_func(dict[weird_classes['weird_bytearray']])
            except Exception as e_async_call:
                print(f"[c5m13] Exception in async task async_call_c5m13___reduce_ex__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c5m13___reduce_ex__", file=stderr)
        fuzzer_async_tasks.append(async_call_c5m13___reduce_ex__)

    try:
        res_c5m14 = callMethod("c5m14", instance_c5_popen, "_launch",
            weird_classes['weird_OrderedDict'],
        verbose=True)
    except Exception as _argexc_c5m14:
        print("[c5m14] call skipped (argument build failed):", repr(_argexc_c5m14), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c5_popen, '_launch')
    except Exception as e_get_target_func:
        print(f"[c5m14] Failed to get attribute _launch from instance_c5_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(DescriptorBomb(),), name='c5m14__launch')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c5m14] Failed to create thread for _launch: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c5m14__launch(target_func=target_func):
            print("Starting async task: async_call_c5m14__launch", file=stderr)
            time.sleep(0.000790) # Small delay
            try:
                target_func(bytearray(b""))
            except Exception as e_async_call:
                print(f"[c5m14] Exception in async task async_call_c5m14__launch: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c5m14__launch", file=stderr)
        fuzzer_async_tasks.append(async_call_c5m14__launch)

    try:
        res_c5m15 = callMethod("c5m15", instance_c5_popen, "__format__",
            "i<3\x97\xC1~S\xF3\x90L",
        verbose=True)
    except Exception as _argexc_c5m15:
        print("[c5m15] call skipped (argument build failed):", repr(_argexc_c5m15), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c5_popen, '__format__')
    except Exception as e_get_target_func:
        print(f"[c5m15] Failed to get attribute __format__ from instance_c5_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=('/tmp/fusil-fixtures/fusil_fixture.bin',), name='c5m15___format__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c5m15] Failed to create thread for __format__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c5m15___format__(target_func=target_func):
            print("Starting async task: async_call_c5m15___format__", file=stderr)
            time.sleep(0.000932) # Small delay
            try:
                target_func(None)
            except Exception as e_async_call:
                print(f"[c5m15] Exception in async task async_call_c5m15___format__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c5m15___format__", file=stderr)
        fuzzer_async_tasks.append(async_call_c5m15___format__)

    print(f"--- Finished fuzzing instance: instance_c5_popen ---", file=stderr)

    del instance_c5_popen # Cleanup instance
    print("[c5] -explicit garbage collection for class instance-", file=stderr)
    collect()

print("[c6] Attempting to instantiate class: Popen", file=stderr)
instance_c6_popen = None # Initialize instance variable
try:
    instance_c6_popen = callFunc('c6_init', 'Popen',
        -sys.float_info.min / 2,
      )
except Exception as e_instantiate:
    instance_c6_popen = None
    print("[c6] Failed to instantiate Popen: {e_instantiate.__class__.__name__} {e_instantiate}", file=stderr)
    instance_c6_popen = None

try:
    print(f"--- (Depth 0) Dispatching Fuzz for: {instance_c6_popen!r} (hint: Popen, prefix: c6_popen_ops) ---", file=stderr)
except Exception as e:
    print(f"--- (Depth 0) Error calling repr() prefix: c6_popen_ops) ---", file=stderr)
if instance_c6_popen is not None:
    if skip_trivial_type(instance_c6_popen):
        print(f'Skipping deep diving on instance_c6_popen {type(instance_c6_popen)}', file=stderr)
    try:
        print(f'Instance {instance_c6_popen!r} (actual type {type(instance_c6_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    except Exception as e:
        print(f'Error printing instance repr() { e } (actual type {type(instance_c6_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    if skip_trivial_type(instance_c6_popen):
        print(f'Skipping deep diving on instance_c6_popen {type(instance_c6_popen)}', file=stderr)
    else:
        print(f'Instance instance_c6_popen (type {type(instance_c6_popen).__name__}) has no specific fuzzer, doing generic calls.', file=stderr)
        c6_popen_ops_generic_methods = []
        try:
            for c6_popen_ops_generic_attr_name in dir(instance_c6_popen):
                if c6_popen_ops_generic_attr_name.startswith('_'): continue
                try:
                    c6_popen_ops_generic_attr_val = getattr(instance_c6_popen, c6_popen_ops_generic_attr_name)
                    if callable(c6_popen_ops_generic_attr_val) and c6_popen_ops_generic_attr_name not in _FUSIL_METHOD_BLACKLIST: c6_popen_ops_generic_methods.append((c6_popen_ops_generic_attr_name, c6_popen_ops_generic_attr_val))
                except Exception: pass
        except Exception: c6_popen_ops_generic_methods = [] # Failed to get methods
        if c6_popen_ops_generic_methods:
            print(f'Found {len(c6_popen_ops_generic_methods)} callable methods for generic fuzzing of instance_c6_popen', file=stderr)
            for _i_c6_popen_ops_generic in range(min(len(c6_popen_ops_generic_methods), 15)):
                c6_popen_ops_generic_method_name_to_call, c6_popen_ops_generic_method_obj_to_call = choice(c6_popen_ops_generic_methods)
                # Conceptual call to generic method fuzzer
                if c6_popen_ops_generic_method_name_to_call not in _FUSIL_METHOD_BLACKLIST: callMethod(f'c6_popen_ops_generic_gen{_i_c6_popen_ops_generic}', instance_c6_popen, c6_popen_ops_generic_method_name_to_call)

if instance_c6_popen is not None and instance_c6_popen is not SENTINEL_VALUE:
    print(f"--- Fuzzing instance: instance_c6_popen (type hint: Popen, prefix: c6m) ---", file=stderr)
    if skip_trivial_type(instance_c6_popen):
        print(f'Skipping deep diving on instance_c6_popen {type(instance_c6_popen)}', file=stderr)
    # General method fuzzing for instance_c6_popen
    try:
        res_c6m1 = callMethod("c6m1", instance_c6_popen, "_launch",
            weird_instances['weird_set_printable'],
        verbose=True)
    except Exception as _argexc_c6m1:
        print("[c6m1] call skipped (argument build failed):", repr(_argexc_c6m1), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c6_popen, '_launch')
    except Exception as e_get_target_func:
        print(f"[c6m1] Failed to get attribute _launch from instance_c6_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(RaisingInstanceCheckType,), name='c6m1__launch')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c6m1] Failed to create thread for _launch: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c6m1__launch(target_func=target_func):
            print("Starting async task: async_call_c6m1__launch", file=stderr)
            time.sleep(0.000858) # Small delay
            try:
                target_func(tricky_mappingproxy)
            except Exception as e_async_call:
                print(f"[c6m1] Exception in async task async_call_c6m1__launch: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c6m1__launch", file=stderr)
        fuzzer_async_tasks.append(async_call_c6m1__launch)

    try:
        res_c6m2 = callMethod("c6m2", instance_c6_popen, "close",
        verbose=True)
    except Exception as _argexc_c6m2:
        print("[c6m2] call skipped (argument build failed):", repr(_argexc_c6m2), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c6_popen, 'close')
    except Exception as e_get_target_func:
        print(f"[c6m2] Failed to get attribute close from instance_c6_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c6m2_close')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c6m2] Failed to create thread for close: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c6m2_close(target_func=target_func):
            print("Starting async task: async_call_c6m2_close", file=stderr)
            time.sleep(0.000505) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c6m2] Exception in async task async_call_c6m2_close: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c6m2_close", file=stderr)
        fuzzer_async_tasks.append(async_call_c6m2_close)

    try:
        res_c6m3 = callMethod("c6m3", instance_c6_popen, "__lt__",
            b"\x40\xB5\x87\xC0\xD9\xF2\x1A",
        verbose=True)
    except Exception as _argexc_c6m3:
        print("[c6m3] call skipped (argument build failed):", repr(_argexc_c6m3), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c6_popen, '__lt__')
    except Exception as e_get_target_func:
        print(f"[c6m3] Failed to get attribute __lt__ from instance_c6_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(ShiftyEq(),), name='c6m3___lt__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c6m3] Failed to create thread for __lt__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c6m3___lt__(target_func=target_func):
            print("Starting async task: async_call_c6m3___lt__", file=stderr)
            time.sleep(0.000476) # Small delay
            try:
                target_func(b"\x56\x06\x4D\x4D\x9F\x3D\x0C\x9F\x97\x7C\xAA\x34\x7E\x6B\x4C\x5D\xC1\x29\x59\x48")
            except Exception as e_async_call:
                print(f"[c6m3] Exception in async task async_call_c6m3___lt__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c6m3___lt__", file=stderr)
        fuzzer_async_tasks.append(async_call_c6m3___lt__)

    try:
        res_c6m4 = callMethod("c6m4", instance_c6_popen, "__getattribute__",
            566221,
        verbose=True)
    except Exception as _argexc_c6m4:
        print("[c6m4] call skipped (argument build failed):", repr(_argexc_c6m4), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c6_popen, '__getattribute__')
    except Exception as e_get_target_func:
        print(f"[c6m4] Failed to get attribute __getattribute__ from instance_c6_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(None,), name='c6m4___getattribute__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c6m4] Failed to create thread for __getattribute__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c6m4___getattribute__(target_func=target_func):
            print("Starting async task: async_call_c6m4___getattribute__", file=stderr)
            time.sleep(0.000257) # Small delay
            try:
                target_func(-9.3122)
            except Exception as e_async_call:
                print(f"[c6m4] Exception in async task async_call_c6m4___getattribute__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c6m4___getattribute__", file=stderr)
        fuzzer_async_tasks.append(async_call_c6m4___getattribute__)

    try:
        res_c6m5 = callMethod("c6m5", instance_c6_popen, "__subclasshook__",
            "\uDC80",
        verbose=True)
    except Exception as _argexc_c6m5:
        print("[c6m5] call skipped (argument build failed):", repr(_argexc_c6m5), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c6_popen, '__subclasshook__')
    except Exception as e_get_target_func:
        print(f"[c6m5] Failed to get attribute __subclasshook__ from instance_c6_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("../LsW/../XJe0uL.cEOJJy_SDoaxG61JWh0GQFX-62Cy/yk/",), name='c6m5___subclasshook__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c6m5] Failed to create thread for __subclasshook__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c6m5___subclasshook__(target_func=target_func):
            print("Starting async task: async_call_c6m5___subclasshook__", file=stderr)
            time.sleep(0.000071) # Small delay
            try:
                target_func(LyingInstanceCheckType)
            except Exception as e_async_call:
                print(f"[c6m5] Exception in async task async_call_c6m5___subclasshook__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c6m5___subclasshook__", file=stderr)
        fuzzer_async_tasks.append(async_call_c6m5___subclasshook__)

    try:
        res_c6m6 = callMethod("c6m6", instance_c6_popen, "__ge__",
            HashBomb(),
        verbose=True)
    except Exception as _argexc_c6m6:
        print("[c6m6] call skipped (argument build failed):", repr(_argexc_c6m6), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c6_popen, '__ge__')
    except Exception as e_get_target_func:
        print(f"[c6m6] Failed to get attribute __ge__ from instance_c6_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(MutatingIterable(),), name='c6m6___ge__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c6m6] Failed to create thread for __ge__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c6m6___ge__(target_func=target_func):
            print("Starting async task: async_call_c6m6___ge__", file=stderr)
            time.sleep(0.000022) # Small delay
            try:
                target_func(list[weird_classes['weird_Counter']] | weird_classes['weird_float'] | big_union)
            except Exception as e_async_call:
                print(f"[c6m6] Exception in async task async_call_c6m6___ge__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c6m6___ge__", file=stderr)
        fuzzer_async_tasks.append(async_call_c6m6___ge__)

    try:
        res_c6m7 = callMethod("c6m7", instance_c6_popen, "terminate",
        verbose=True)
    except Exception as _argexc_c6m7:
        print("[c6m7] call skipped (argument build failed):", repr(_argexc_c6m7), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c6_popen, 'terminate')
    except Exception as e_get_target_func:
        print(f"[c6m7] Failed to get attribute terminate from instance_c6_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c6m7_terminate')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c6m7] Failed to create thread for terminate: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c6m7_terminate(target_func=target_func):
            print("Starting async task: async_call_c6m7_terminate", file=stderr)
            time.sleep(0.000032) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c6m7] Exception in async task async_call_c6m7_terminate: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c6m7_terminate", file=stderr)
        fuzzer_async_tasks.append(async_call_c6m7_terminate)

    try:
        res_c6m8 = callMethod("c6m8", instance_c6_popen, "poll",
            r"WN..SIA\Z.k.iNzp.eA\sS*YmEnXws",
        verbose=True)
    except Exception as _argexc_c6m8:
        print("[c6m8] call skipped (argument build failed):", repr(_argexc_c6m8), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c6_popen, 'poll')
    except Exception as e_get_target_func:
        print(f"[c6m8] Failed to get attribute poll from instance_c6_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("\xD8\xB8",), name='c6m8_poll')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c6m8] Failed to create thread for poll: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c6m8_poll(target_func=target_func):
            print("Starting async task: async_call_c6m8_poll", file=stderr)
            time.sleep(0.000201) # Small delay
            try:
                target_func(DescriptorBomb())
            except Exception as e_async_call:
                print(f"[c6m8] Exception in async task async_call_c6m8_poll: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c6m8_poll", file=stderr)
        fuzzer_async_tasks.append(async_call_c6m8_poll)

    try:
        res_c6m9 = callMethod("c6m9", instance_c6_popen, "kill",
        verbose=True)
    except Exception as _argexc_c6m9:
        print("[c6m9] call skipped (argument build failed):", repr(_argexc_c6m9), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c6_popen, 'kill')
    except Exception as e_get_target_func:
        print(f"[c6m9] Failed to get attribute kill from instance_c6_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c6m9_kill')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c6m9] Failed to create thread for kill: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c6m9_kill(target_func=target_func):
            print("Starting async task: async_call_c6m9_kill", file=stderr)
            time.sleep(0.000671) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c6m9] Exception in async task async_call_c6m9_kill: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c6m9_kill", file=stderr)
        fuzzer_async_tasks.append(async_call_c6m9_kill)

    try:
        res_c6m10 = callMethod("c6m10", instance_c6_popen, "__ge__",
            -10 ** (sys.int_info.default_max_str_digits),
        verbose=True)
    except Exception as _argexc_c6m10:
        print("[c6m10] call skipped (argument build failed):", repr(_argexc_c6m10), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c6_popen, '__ge__')
    except Exception as e_get_target_func:
        print(f"[c6m10] Failed to get attribute __ge__ from instance_c6_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(14,), name='c6m10___ge__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c6m10] Failed to create thread for __ge__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c6m10___ge__(target_func=target_func):
            print("Starting async task: async_call_c6m10___ge__", file=stderr)
            time.sleep(0.000556) # Small delay
            try:
                target_func(HashBomb())
            except Exception as e_async_call:
                print(f"[c6m10] Exception in async task async_call_c6m10___ge__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c6m10___ge__", file=stderr)
        fuzzer_async_tasks.append(async_call_c6m10___ge__)

    try:
        res_c6m11 = callMethod("c6m11", instance_c6_popen, "__reduce__",
        verbose=True)
    except Exception as _argexc_c6m11:
        print("[c6m11] call skipped (argument build failed):", repr(_argexc_c6m11), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c6_popen, '__reduce__')
    except Exception as e_get_target_func:
        print(f"[c6m11] Failed to get attribute __reduce__ from instance_c6_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c6m11___reduce__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c6m11] Failed to create thread for __reduce__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c6m11___reduce__(target_func=target_func):
            print("Starting async task: async_call_c6m11___reduce__", file=stderr)
            time.sleep(0.000328) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c6m11] Exception in async task async_call_c6m11___reduce__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c6m11___reduce__", file=stderr)
        fuzzer_async_tasks.append(async_call_c6m11___reduce__)

    try:
        res_c6m12 = callMethod("c6m12", instance_c6_popen, "__getattribute__",
            HashBomb(),
        verbose=True)
    except Exception as _argexc_c6m12:
        print("[c6m12] call skipped (argument build failed):", repr(_argexc_c6m12), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c6_popen, '__getattribute__')
    except Exception as e_get_target_func:
        print(f"[c6m12] Failed to get attribute __getattribute__ from instance_c6_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("\u10AA\u0890\uE827\u2AA8\u99FC\uAF5B\uB93D\u91D1\u60A5\uA683\u4859\uEE7C\uE794\u7EA4\uA5B8\uC20D",), name='c6m12___getattribute__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c6m12] Failed to create thread for __getattribute__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c6m12___getattribute__(target_func=target_func):
            print("Starting async task: async_call_c6m12___getattribute__", file=stderr)
            time.sleep(0.000965) # Small delay
            try:
                target_func("\x92\x97\xBB")
            except Exception as e_async_call:
                print(f"[c6m12] Exception in async task async_call_c6m12___getattribute__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c6m12___getattribute__", file=stderr)
        fuzzer_async_tasks.append(async_call_c6m12___getattribute__)

    try:
        res_c6m13 = callMethod("c6m13", instance_c6_popen, "__subclasshook__",
            '/tmp/fusil-fixtures/fusil_fixture.txt',
            errback,
        verbose=True)
    except Exception as _argexc_c6m13:
        print("[c6m13] call skipped (argument build failed):", repr(_argexc_c6m13), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c6_popen, '__subclasshook__')
    except Exception as e_get_target_func:
        print(f"[c6m13] Failed to get attribute __subclasshook__ from instance_c6_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(list[weird_classes['weird_Queue']] | weird_classes['weird_list'] | big_union, -794), name='c6m13___subclasshook__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c6m13] Failed to create thread for __subclasshook__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c6m13___subclasshook__(target_func=target_func):
            print("Starting async task: async_call_c6m13___subclasshook__", file=stderr)
            time.sleep(0.000623) # Small delay
            try:
                target_func("\x06\xE6\xDD\x8ED\x1E\xEC", errback)
            except Exception as e_async_call:
                print(f"[c6m13] Exception in async task async_call_c6m13___subclasshook__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c6m13___subclasshook__", file=stderr)
        fuzzer_async_tasks.append(async_call_c6m13___subclasshook__)

    try:
        res_c6m14 = callMethod("c6m14", instance_c6_popen, "poll",
            weird_instances['weird_int_-2**63'],
        verbose=True)
    except Exception as _argexc_c6m14:
        print("[c6m14] call skipped (argument build failed):", repr(_argexc_c6m14), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c6_popen, 'poll')
    except Exception as e_get_target_func:
        print(f"[c6m14] Failed to get attribute poll from instance_c6_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(EqBomb(),), name='c6m14_poll')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c6m14] Failed to create thread for poll: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c6m14_poll(target_func=target_func):
            print("Starting async task: async_call_c6m14_poll", file=stderr)
            time.sleep(0.000384) # Small delay
            try:
                target_func(float("nan"))
            except Exception as e_async_call:
                print(f"[c6m14] Exception in async task async_call_c6m14_poll: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c6m14_poll", file=stderr)
        fuzzer_async_tasks.append(async_call_c6m14_poll)

    try:
        res_c6m15 = callMethod("c6m15", instance_c6_popen, "__dir__",
        verbose=True)
    except Exception as _argexc_c6m15:
        print("[c6m15] call skipped (argument build failed):", repr(_argexc_c6m15), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c6_popen, '__dir__')
    except Exception as e_get_target_func:
        print(f"[c6m15] Failed to get attribute __dir__ from instance_c6_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c6m15___dir__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c6m15] Failed to create thread for __dir__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c6m15___dir__(target_func=target_func):
            print("Starting async task: async_call_c6m15___dir__", file=stderr)
            time.sleep(0.000917) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c6m15] Exception in async task async_call_c6m15___dir__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c6m15___dir__", file=stderr)
        fuzzer_async_tasks.append(async_call_c6m15___dir__)

    print(f"--- Finished fuzzing instance: instance_c6_popen ---", file=stderr)

    del instance_c6_popen # Cleanup instance
    print("[c6] -explicit garbage collection for class instance-", file=stderr)
    collect()

print("[c7] Attempting to instantiate class: Popen", file=stderr)
instance_c7_popen = None # Initialize instance variable
try:
    instance_c7_popen = callFunc('c7_init', 'Popen',
        bytearray(b"test"),
      )
except Exception as e_instantiate:
    instance_c7_popen = None
    print("[c7] Failed to instantiate Popen: {e_instantiate.__class__.__name__} {e_instantiate}", file=stderr)
    instance_c7_popen = None

try:
    print(f"--- (Depth 0) Dispatching Fuzz for: {instance_c7_popen!r} (hint: Popen, prefix: c7_popen_ops) ---", file=stderr)
except Exception as e:
    print(f"--- (Depth 0) Error calling repr() prefix: c7_popen_ops) ---", file=stderr)
if instance_c7_popen is not None:
    if skip_trivial_type(instance_c7_popen):
        print(f'Skipping deep diving on instance_c7_popen {type(instance_c7_popen)}', file=stderr)
    try:
        print(f'Instance {instance_c7_popen!r} (actual type {type(instance_c7_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    except Exception as e:
        print(f'Error printing instance repr() { e } (actual type {type(instance_c7_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    if skip_trivial_type(instance_c7_popen):
        print(f'Skipping deep diving on instance_c7_popen {type(instance_c7_popen)}', file=stderr)
    else:
        print(f'Instance instance_c7_popen (type {type(instance_c7_popen).__name__}) has no specific fuzzer, doing generic calls.', file=stderr)
        c7_popen_ops_generic_methods = []
        try:
            for c7_popen_ops_generic_attr_name in dir(instance_c7_popen):
                if c7_popen_ops_generic_attr_name.startswith('_'): continue
                try:
                    c7_popen_ops_generic_attr_val = getattr(instance_c7_popen, c7_popen_ops_generic_attr_name)
                    if callable(c7_popen_ops_generic_attr_val) and c7_popen_ops_generic_attr_name not in _FUSIL_METHOD_BLACKLIST: c7_popen_ops_generic_methods.append((c7_popen_ops_generic_attr_name, c7_popen_ops_generic_attr_val))
                except Exception: pass
        except Exception: c7_popen_ops_generic_methods = [] # Failed to get methods
        if c7_popen_ops_generic_methods:
            print(f'Found {len(c7_popen_ops_generic_methods)} callable methods for generic fuzzing of instance_c7_popen', file=stderr)
            for _i_c7_popen_ops_generic in range(min(len(c7_popen_ops_generic_methods), 15)):
                c7_popen_ops_generic_method_name_to_call, c7_popen_ops_generic_method_obj_to_call = choice(c7_popen_ops_generic_methods)
                # Conceptual call to generic method fuzzer
                if c7_popen_ops_generic_method_name_to_call not in _FUSIL_METHOD_BLACKLIST: callMethod(f'c7_popen_ops_generic_gen{_i_c7_popen_ops_generic}', instance_c7_popen, c7_popen_ops_generic_method_name_to_call)

if instance_c7_popen is not None and instance_c7_popen is not SENTINEL_VALUE:
    print(f"--- Fuzzing instance: instance_c7_popen (type hint: Popen, prefix: c7m) ---", file=stderr)
    if skip_trivial_type(instance_c7_popen):
        print(f'Skipping deep diving on instance_c7_popen {type(instance_c7_popen)}', file=stderr)
    # General method fuzzing for instance_c7_popen
    try:
        res_c7m1 = callMethod("c7m1", instance_c7_popen, "__reduce_ex__",
        verbose=True)
    except Exception as _argexc_c7m1:
        print("[c7m1] call skipped (argument build failed):", repr(_argexc_c7m1), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c7_popen, '__reduce_ex__')
    except Exception as e_get_target_func:
        print(f"[c7m1] Failed to get attribute __reduce_ex__ from instance_c7_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c7m1___reduce_ex__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c7m1] Failed to create thread for __reduce_ex__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c7m1___reduce_ex__(target_func=target_func):
            print("Starting async task: async_call_c7m1___reduce_ex__", file=stderr)
            time.sleep(0.000040) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c7m1] Exception in async task async_call_c7m1___reduce_ex__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c7m1___reduce_ex__", file=stderr)
        fuzzer_async_tasks.append(async_call_c7m1___reduce_ex__)

    try:
        res_c7m2 = callMethod("c7m2", instance_c7_popen, "__reduce__",
        verbose=True)
    except Exception as _argexc_c7m2:
        print("[c7m2] call skipped (argument build failed):", repr(_argexc_c7m2), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c7_popen, '__reduce__')
    except Exception as e_get_target_func:
        print(f"[c7m2] Failed to get attribute __reduce__ from instance_c7_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c7m2___reduce__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c7m2] Failed to create thread for __reduce__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c7m2___reduce__(target_func=target_func):
            print("Starting async task: async_call_c7m2___reduce__", file=stderr)
            time.sleep(0.000755) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c7m2] Exception in async task async_call_c7m2___reduce__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c7m2___reduce__", file=stderr)
        fuzzer_async_tasks.append(async_call_c7m2___reduce__)

    try:
        res_c7m3 = callMethod("c7m3", instance_c7_popen, "duplicate_for_child",
            r"L\d.ikjRugNOLndtWqILSZw.cKxw.YQOGuZEjTiEDle+",
        verbose=True)
    except Exception as _argexc_c7m3:
        print("[c7m3] call skipped (argument build failed):", repr(_argexc_c7m3), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c7_popen, 'duplicate_for_child')
    except Exception as e_get_target_func:
        print(f"[c7m3] Failed to get attribute duplicate_for_child from instance_c7_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(0,), name='c7m3_duplicate_for_child')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c7m3] Failed to create thread for duplicate_for_child: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c7m3_duplicate_for_child(target_func=target_func):
            print("Starting async task: async_call_c7m3_duplicate_for_child", file=stderr)
            time.sleep(0.000167) # Small delay
            try:
                target_func(19)
            except Exception as e_async_call:
                print(f"[c7m3] Exception in async task async_call_c7m3_duplicate_for_child: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c7m3_duplicate_for_child", file=stderr)
        fuzzer_async_tasks.append(async_call_c7m3_duplicate_for_child)

    try:
        res_c7m4 = callMethod("c7m4", instance_c7_popen, "__gt__",
            LenBomb(),
        verbose=True)
    except Exception as _argexc_c7m4:
        print("[c7m4] call skipped (argument build failed):", repr(_argexc_c7m4), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c7_popen, '__gt__')
    except Exception as e_get_target_func:
        print(f"[c7m4] Failed to get attribute __gt__ from instance_c7_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(IndexBomb(),), name='c7m4___gt__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c7m4] Failed to create thread for __gt__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c7m4___gt__(target_func=target_func):
            print("Starting async task: async_call_c7m4___gt__", file=stderr)
            time.sleep(0.000169) # Small delay
            try:
                target_func("\U0010FFFF")
            except Exception as e_async_call:
                print(f"[c7m4] Exception in async task async_call_c7m4___gt__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c7m4___gt__", file=stderr)
        fuzzer_async_tasks.append(async_call_c7m4___gt__)

    try:
        res_c7m5 = callMethod("c7m5", instance_c7_popen, "__str__",
        verbose=True)
    except Exception as _argexc_c7m5:
        print("[c7m5] call skipped (argument build failed):", repr(_argexc_c7m5), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c7_popen, '__str__')
    except Exception as e_get_target_func:
        print(f"[c7m5] Failed to get attribute __str__ from instance_c7_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c7m5___str__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c7m5] Failed to create thread for __str__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c7m5___str__(target_func=target_func):
            print("Starting async task: async_call_c7m5___str__", file=stderr)
            time.sleep(0.000218) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c7m5] Exception in async task async_call_c7m5___str__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c7m5___str__", file=stderr)
        fuzzer_async_tasks.append(async_call_c7m5___str__)

    try:
        res_c7m6 = callMethod("c7m6", instance_c7_popen, "close",
        verbose=True)
    except Exception as _argexc_c7m6:
        print("[c7m6] call skipped (argument build failed):", repr(_argexc_c7m6), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c7_popen, 'close')
    except Exception as e_get_target_func:
        print(f"[c7m6] Failed to get attribute close from instance_c7_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c7m6_close')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c7m6] Failed to create thread for close: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c7m6_close(target_func=target_func):
            print("Starting async task: async_call_c7m6_close", file=stderr)
            time.sleep(0.000771) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c7m6] Exception in async task async_call_c7m6_close: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c7m6_close", file=stderr)
        fuzzer_async_tasks.append(async_call_c7m6_close)

    try:
        res_c7m7 = callMethod("c7m7", instance_c7_popen, "__getattribute__",
            "\xCFC\xC3\xD4",
        verbose=True)
    except Exception as _argexc_c7m7:
        print("[c7m7] call skipped (argument build failed):", repr(_argexc_c7m7), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c7_popen, '__getattribute__')
    except Exception as e_get_target_func:
        print(f"[c7m7] Failed to get attribute __getattribute__ from instance_c7_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(None,), name='c7m7___getattribute__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c7m7] Failed to create thread for __getattribute__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c7m7___getattribute__(target_func=target_func):
            print("Starting async task: async_call_c7m7___getattribute__", file=stderr)
            time.sleep(0.000018) # Small delay
            try:
                target_func(ReentrantClearDict())
            except Exception as e_async_call:
                print(f"[c7m7] Exception in async task async_call_c7m7___getattribute__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c7m7___getattribute__", file=stderr)
        fuzzer_async_tasks.append(async_call_c7m7___getattribute__)

    try:
        res_c7m8 = callMethod("c7m8", instance_c7_popen, "__format__",
            dict[weird_classes['weird_Queue']] | weird_classes['weird_object'] | big_union,
        verbose=True)
    except Exception as _argexc_c7m8:
        print("[c7m8] call skipped (argument build failed):", repr(_argexc_c7m8), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c7_popen, '__format__')
    except Exception as e_get_target_func:
        print(f"[c7m8] Failed to get attribute __format__ from instance_c7_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(MutatingHash(),), name='c7m8___format__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c7m8] Failed to create thread for __format__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c7m8___format__(target_func=target_func):
            print("Starting async task: async_call_c7m8___format__", file=stderr)
            time.sleep(0.000290) # Small delay
            try:
                target_func("azkQ30IaQjp4XRbQN-1yqUv-WGUo/../..//../N")
            except Exception as e_async_call:
                print(f"[c7m8] Exception in async task async_call_c7m8___format__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c7m8___format__", file=stderr)
        fuzzer_async_tasks.append(async_call_c7m8___format__)

    try:
        res_c7m9 = callMethod("c7m9", instance_c7_popen, "__delattr__",
            StatefulHashType,
        verbose=True)
    except Exception as _argexc_c7m9:
        print("[c7m9] call skipped (argument build failed):", repr(_argexc_c7m9), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c7_popen, '__delattr__')
    except Exception as e_get_target_func:
        print(f"[c7m9] Failed to get attribute __delattr__ from instance_c7_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(lambda: None,), name='c7m9___delattr__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c7m9] Failed to create thread for __delattr__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c7m9___delattr__(target_func=target_func):
            print("Starting async task: async_call_c7m9___delattr__", file=stderr)
            time.sleep(0.000236) # Small delay
            try:
                target_func('/tmp/fusil-fixtures/fusil_fixture.txt')
            except Exception as e_async_call:
                print(f"[c7m9] Exception in async task async_call_c7m9___delattr__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c7m9___delattr__", file=stderr)
        fuzzer_async_tasks.append(async_call_c7m9___delattr__)

    try:
        res_c7m10 = callMethod("c7m10", instance_c7_popen, "__reduce__",
        verbose=True)
    except Exception as _argexc_c7m10:
        print("[c7m10] call skipped (argument build failed):", repr(_argexc_c7m10), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c7_popen, '__reduce__')
    except Exception as e_get_target_func:
        print(f"[c7m10] Failed to get attribute __reduce__ from instance_c7_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c7m10___reduce__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c7m10] Failed to create thread for __reduce__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c7m10___reduce__(target_func=target_func):
            print("Starting async task: async_call_c7m10___reduce__", file=stderr)
            time.sleep(0.000442) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c7m10] Exception in async task async_call_c7m10___reduce__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c7m10___reduce__", file=stderr)
        fuzzer_async_tasks.append(async_call_c7m10___reduce__)

    try:
        res_c7m11 = callMethod("c7m11", instance_c7_popen, "__str__",
        verbose=True)
    except Exception as _argexc_c7m11:
        print("[c7m11] call skipped (argument build failed):", repr(_argexc_c7m11), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c7_popen, '__str__')
    except Exception as e_get_target_func:
        print(f"[c7m11] Failed to get attribute __str__ from instance_c7_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c7m11___str__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c7m11] Failed to create thread for __str__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c7m11___str__(target_func=target_func):
            print("Starting async task: async_call_c7m11___str__", file=stderr)
            time.sleep(0.000519) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c7m11] Exception in async task async_call_c7m11___str__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c7m11___str__", file=stderr)
        fuzzer_async_tasks.append(async_call_c7m11___str__)

    try:
        res_c7m12 = callMethod("c7m12", instance_c7_popen, "kill",
        verbose=True)
    except Exception as _argexc_c7m12:
        print("[c7m12] call skipped (argument build failed):", repr(_argexc_c7m12), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c7_popen, 'kill')
    except Exception as e_get_target_func:
        print(f"[c7m12] Failed to get attribute kill from instance_c7_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c7m12_kill')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c7m12] Failed to create thread for kill: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c7m12_kill(target_func=target_func):
            print("Starting async task: async_call_c7m12_kill", file=stderr)
            time.sleep(0.000633) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c7m12] Exception in async task async_call_c7m12_kill: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c7m12_kill", file=stderr)
        fuzzer_async_tasks.append(async_call_c7m12_kill)

    try:
        res_c7m13 = callMethod("c7m13", instance_c7_popen, "_send_signal",
            '/tmp/fusil-fixtures/fusil_fixture.txt',
        verbose=True)
    except Exception as _argexc_c7m13:
        print("[c7m13] call skipped (argument build failed):", repr(_argexc_c7m13), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c7_popen, '_send_signal')
    except Exception as e_get_target_func:
        print(f"[c7m13] Failed to get attribute _send_signal from instance_c7_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(weird_classes['weird_bytearray'],), name='c7m13__send_signal')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c7m13] Failed to create thread for _send_signal: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c7m13__send_signal(target_func=target_func):
            print("Starting async task: async_call_c7m13__send_signal", file=stderr)
            time.sleep(0.000087) # Small delay
            try:
                target_func("\uD5C2\u91B3\u6273\uEE4A\u9E91\u1E28\u7648\uF2D1\uC0B3\u9441\u0E27\u62AE\uF738\u6AAD\u1957")
            except Exception as e_async_call:
                print(f"[c7m13] Exception in async task async_call_c7m13__send_signal: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c7m13__send_signal", file=stderr)
        fuzzer_async_tasks.append(async_call_c7m13__send_signal)

    try:
        res_c7m14 = callMethod("c7m14", instance_c7_popen, "__reduce__",
        verbose=True)
    except Exception as _argexc_c7m14:
        print("[c7m14] call skipped (argument build failed):", repr(_argexc_c7m14), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c7_popen, '__reduce__')
    except Exception as e_get_target_func:
        print(f"[c7m14] Failed to get attribute __reduce__ from instance_c7_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c7m14___reduce__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c7m14] Failed to create thread for __reduce__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c7m14___reduce__(target_func=target_func):
            print("Starting async task: async_call_c7m14___reduce__", file=stderr)
            time.sleep(0.000728) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c7m14] Exception in async task async_call_c7m14___reduce__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c7m14___reduce__", file=stderr)
        fuzzer_async_tasks.append(async_call_c7m14___reduce__)

    try:
        res_c7m15 = callMethod("c7m15", instance_c7_popen, "__hash__",
        verbose=True)
    except Exception as _argexc_c7m15:
        print("[c7m15] call skipped (argument build failed):", repr(_argexc_c7m15), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c7_popen, '__hash__')
    except Exception as e_get_target_func:
        print(f"[c7m15] Failed to get attribute __hash__ from instance_c7_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c7m15___hash__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c7m15] Failed to create thread for __hash__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c7m15___hash__(target_func=target_func):
            print("Starting async task: async_call_c7m15___hash__", file=stderr)
            time.sleep(0.000299) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c7m15] Exception in async task async_call_c7m15___hash__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c7m15___hash__", file=stderr)
        fuzzer_async_tasks.append(async_call_c7m15___hash__)

    print(f"--- Finished fuzzing instance: instance_c7_popen ---", file=stderr)

    del instance_c7_popen # Cleanup instance
    print("[c7] -explicit garbage collection for class instance-", file=stderr)
    collect()

print("[c8] Attempting to instantiate class: Popen", file=stderr)
instance_c8_popen = None # Initialize instance variable
try:
    instance_c8_popen = callFunc('c8_init', 'Popen',
        7,
      )
except Exception as e_instantiate:
    instance_c8_popen = None
    print("[c8] Failed to instantiate Popen: {e_instantiate.__class__.__name__} {e_instantiate}", file=stderr)
    instance_c8_popen = None

try:
    print(f"--- (Depth 0) Dispatching Fuzz for: {instance_c8_popen!r} (hint: Popen, prefix: c8_popen_ops) ---", file=stderr)
except Exception as e:
    print(f"--- (Depth 0) Error calling repr() prefix: c8_popen_ops) ---", file=stderr)
if instance_c8_popen is not None:
    if skip_trivial_type(instance_c8_popen):
        print(f'Skipping deep diving on instance_c8_popen {type(instance_c8_popen)}', file=stderr)
    try:
        print(f'Instance {instance_c8_popen!r} (actual type {type(instance_c8_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    except Exception as e:
        print(f'Error printing instance repr() { e } (actual type {type(instance_c8_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    if skip_trivial_type(instance_c8_popen):
        print(f'Skipping deep diving on instance_c8_popen {type(instance_c8_popen)}', file=stderr)
    else:
        print(f'Instance instance_c8_popen (type {type(instance_c8_popen).__name__}) has no specific fuzzer, doing generic calls.', file=stderr)
        c8_popen_ops_generic_methods = []
        try:
            for c8_popen_ops_generic_attr_name in dir(instance_c8_popen):
                if c8_popen_ops_generic_attr_name.startswith('_'): continue
                try:
                    c8_popen_ops_generic_attr_val = getattr(instance_c8_popen, c8_popen_ops_generic_attr_name)
                    if callable(c8_popen_ops_generic_attr_val) and c8_popen_ops_generic_attr_name not in _FUSIL_METHOD_BLACKLIST: c8_popen_ops_generic_methods.append((c8_popen_ops_generic_attr_name, c8_popen_ops_generic_attr_val))
                except Exception: pass
        except Exception: c8_popen_ops_generic_methods = [] # Failed to get methods
        if c8_popen_ops_generic_methods:
            print(f'Found {len(c8_popen_ops_generic_methods)} callable methods for generic fuzzing of instance_c8_popen', file=stderr)
            for _i_c8_popen_ops_generic in range(min(len(c8_popen_ops_generic_methods), 15)):
                c8_popen_ops_generic_method_name_to_call, c8_popen_ops_generic_method_obj_to_call = choice(c8_popen_ops_generic_methods)
                # Conceptual call to generic method fuzzer
                if c8_popen_ops_generic_method_name_to_call not in _FUSIL_METHOD_BLACKLIST: callMethod(f'c8_popen_ops_generic_gen{_i_c8_popen_ops_generic}', instance_c8_popen, c8_popen_ops_generic_method_name_to_call)

if instance_c8_popen is not None and instance_c8_popen is not SENTINEL_VALUE:
    print(f"--- Fuzzing instance: instance_c8_popen (type hint: Popen, prefix: c8m) ---", file=stderr)
    if skip_trivial_type(instance_c8_popen):
        print(f'Skipping deep diving on instance_c8_popen {type(instance_c8_popen)}', file=stderr)
    # General method fuzzing for instance_c8_popen
    try:
        res_c8m1 = callMethod("c8m1", instance_c8_popen, "__new__",
            '/tmp/fusil-fixtures/fusil_fixture.bin',
            Liar2,
            weird_instances['weird_str_types'],
            IndexBomb(),
        verbose=True)
    except Exception as _argexc_c8m1:
        print("[c8m1] call skipped (argument build failed):", repr(_argexc_c8m1), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c8_popen, '__new__')
    except Exception as e_get_target_func:
        print(f"[c8m1] Failed to get attribute __new__ from instance_c8_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(-20531, b"\x2A\xF9\x6B\xE8\xC9\xFD\x2E\x94\xA3\x2C\x37\x1B\x1E", 8813029579940215, errback), name='c8m1___new__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c8m1] Failed to create thread for __new__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c8m1___new__(target_func=target_func):
            print("Starting async task: async_call_c8m1___new__", file=stderr)
            time.sleep(0.000663) # Small delay
            try:
                target_func(-11, errback, ReentrantClearList(), bytearray(b"test"))
            except Exception as e_async_call:
                print(f"[c8m1] Exception in async task async_call_c8m1___new__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c8m1___new__", file=stderr)
        fuzzer_async_tasks.append(async_call_c8m1___new__)

    try:
        res_c8m2 = callMethod("c8m2", instance_c8_popen, "__eq__",
            "j\xD1tPE\xF3=\x0B%\xB0\xF0JCE\x10e\xAC\x10",
        verbose=True)
    except Exception as _argexc_c8m2:
        print("[c8m2] call skipped (argument build failed):", repr(_argexc_c8m2), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c8_popen, '__eq__')
    except Exception as e_get_target_func:
        print(f"[c8m2] Failed to get attribute __eq__ from instance_c8_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(dict[weird_classes['weird_object']] | weird_classes['weird_int'] | big_union,), name='c8m2___eq__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c8m2] Failed to create thread for __eq__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c8m2___eq__(target_func=target_func):
            print("Starting async task: async_call_c8m2___eq__", file=stderr)
            time.sleep(0.000655) # Small delay
            try:
                target_func(LyingLen())
            except Exception as e_async_call:
                print(f"[c8m2] Exception in async task async_call_c8m2___eq__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c8m2___eq__", file=stderr)
        fuzzer_async_tasks.append(async_call_c8m2___eq__)

    try:
        res_c8m3 = callMethod("c8m3", instance_c8_popen, "__str__",
        verbose=True)
    except Exception as _argexc_c8m3:
        print("[c8m3] call skipped (argument build failed):", repr(_argexc_c8m3), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c8_popen, '__str__')
    except Exception as e_get_target_func:
        print(f"[c8m3] Failed to get attribute __str__ from instance_c8_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c8m3___str__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c8m3] Failed to create thread for __str__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c8m3___str__(target_func=target_func):
            print("Starting async task: async_call_c8m3___str__", file=stderr)
            time.sleep(0.000219) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c8m3] Exception in async task async_call_c8m3___str__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c8m3___str__", file=stderr)
        fuzzer_async_tasks.append(async_call_c8m3___str__)

    try:
        res_c8m4 = callMethod("c8m4", instance_c8_popen, "kill",
        verbose=True)
    except Exception as _argexc_c8m4:
        print("[c8m4] call skipped (argument build failed):", repr(_argexc_c8m4), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c8_popen, 'kill')
    except Exception as e_get_target_func:
        print(f"[c8m4] Failed to get attribute kill from instance_c8_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c8m4_kill')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c8m4] Failed to create thread for kill: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c8m4_kill(target_func=target_func):
            print("Starting async task: async_call_c8m4_kill", file=stderr)
            time.sleep(0.000951) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c8m4] Exception in async task async_call_c8m4_kill: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c8m4_kill", file=stderr)
        fuzzer_async_tasks.append(async_call_c8m4_kill)

    try:
        res_c8m5 = callMethod("c8m5", instance_c8_popen, "close",
        verbose=True)
    except Exception as _argexc_c8m5:
        print("[c8m5] call skipped (argument build failed):", repr(_argexc_c8m5), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c8_popen, 'close')
    except Exception as e_get_target_func:
        print(f"[c8m5] Failed to get attribute close from instance_c8_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c8m5_close')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c8m5] Failed to create thread for close: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c8m5_close(target_func=target_func):
            print("Starting async task: async_call_c8m5_close", file=stderr)
            time.sleep(0.000901) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c8m5] Exception in async task async_call_c8m5_close: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c8m5_close", file=stderr)
        fuzzer_async_tasks.append(async_call_c8m5_close)

    try:
        res_c8m6 = callMethod("c8m6", instance_c8_popen, "duplicate_for_child",
            -63.369,
        verbose=True)
    except Exception as _argexc_c8m6:
        print("[c8m6] call skipped (argument build failed):", repr(_argexc_c8m6), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c8_popen, 'duplicate_for_child')
    except Exception as e_get_target_func:
        print(f"[c8m6] Failed to get attribute duplicate_for_child from instance_c8_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("\uDC80",), name='c8m6_duplicate_for_child')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c8m6] Failed to create thread for duplicate_for_child: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c8m6_duplicate_for_child(target_func=target_func):
            print("Starting async task: async_call_c8m6_duplicate_for_child", file=stderr)
            time.sleep(0.000585) # Small delay
            try:
                target_func(list[weird_classes['weird_OrderedDict']] | weird_classes['weird_Queue'] | big_union)
            except Exception as e_async_call:
                print(f"[c8m6] Exception in async task async_call_c8m6_duplicate_for_child: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c8m6_duplicate_for_child", file=stderr)
        fuzzer_async_tasks.append(async_call_c8m6_duplicate_for_child)

    try:
        res_c8m7 = callMethod("c8m7", instance_c8_popen, "__eq__",
            dict[weird_classes['weird_bytes']],
        verbose=True)
    except Exception as _argexc_c8m7:
        print("[c8m7] call skipped (argument build failed):", repr(_argexc_c8m7), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c8_popen, '__eq__')
    except Exception as e_get_target_func:
        print(f"[c8m7] Failed to get attribute __eq__ from instance_c8_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(r"zqQ\AZqb\Z\w\ZD.W\A.xg+qi",), name='c8m7___eq__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c8m7] Failed to create thread for __eq__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c8m7___eq__(target_func=target_func):
            print("Starting async task: async_call_c8m7___eq__", file=stderr)
            time.sleep(0.000949) # Small delay
            try:
                target_func(None)
            except Exception as e_async_call:
                print(f"[c8m7] Exception in async task async_call_c8m7___eq__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c8m7___eq__", file=stderr)
        fuzzer_async_tasks.append(async_call_c8m7___eq__)

    try:
        res_c8m8 = callMethod("c8m8", instance_c8_popen, "__str__",
        verbose=True)
    except Exception as _argexc_c8m8:
        print("[c8m8] call skipped (argument build failed):", repr(_argexc_c8m8), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c8_popen, '__str__')
    except Exception as e_get_target_func:
        print(f"[c8m8] Failed to get attribute __str__ from instance_c8_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c8m8___str__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c8m8] Failed to create thread for __str__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c8m8___str__(target_func=target_func):
            print("Starting async task: async_call_c8m8___str__", file=stderr)
            time.sleep(0.000079) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c8m8] Exception in async task async_call_c8m8___str__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c8m8___str__", file=stderr)
        fuzzer_async_tasks.append(async_call_c8m8___str__)

    try:
        res_c8m9 = callMethod("c8m9", instance_c8_popen, "__repr__",
        verbose=True)
    except Exception as _argexc_c8m9:
        print("[c8m9] call skipped (argument build failed):", repr(_argexc_c8m9), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c8_popen, '__repr__')
    except Exception as e_get_target_func:
        print(f"[c8m9] Failed to get attribute __repr__ from instance_c8_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c8m9___repr__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c8m9] Failed to create thread for __repr__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c8m9___repr__(target_func=target_func):
            print("Starting async task: async_call_c8m9___repr__", file=stderr)
            time.sleep(0.000541) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c8m9] Exception in async task async_call_c8m9___repr__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c8m9___repr__", file=stderr)
        fuzzer_async_tasks.append(async_call_c8m9___repr__)

    try:
        res_c8m10 = callMethod("c8m10", instance_c8_popen, "__gt__",
            Template("\x00", Interpolation(weird_instances['weird_float_2**31-1'], "name")),
        verbose=True)
    except Exception as _argexc_c8m10:
        print("[c8m10] call skipped (argument build failed):", repr(_argexc_c8m10), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c8_popen, '__gt__')
    except Exception as e_get_target_func:
        print(f"[c8m10] Failed to get attribute __gt__ from instance_c8_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(EqBomb(),), name='c8m10___gt__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c8m10] Failed to create thread for __gt__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c8m10___gt__(target_func=target_func):
            print("Starting async task: async_call_c8m10___gt__", file=stderr)
            time.sleep(0.000084) # Small delay
            try:
                target_func(r"KI.dqLTOe+gmC+gsXE*W")
            except Exception as e_async_call:
                print(f"[c8m10] Exception in async task async_call_c8m10___gt__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c8m10___gt__", file=stderr)
        fuzzer_async_tasks.append(async_call_c8m10___gt__)

    try:
        res_c8m11 = callMethod("c8m11", instance_c8_popen, "__getstate__",
        verbose=True)
    except Exception as _argexc_c8m11:
        print("[c8m11] call skipped (argument build failed):", repr(_argexc_c8m11), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c8_popen, '__getstate__')
    except Exception as e_get_target_func:
        print(f"[c8m11] Failed to get attribute __getstate__ from instance_c8_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c8m11___getstate__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c8m11] Failed to create thread for __getstate__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c8m11___getstate__(target_func=target_func):
            print("Starting async task: async_call_c8m11___getstate__", file=stderr)
            time.sleep(0.000325) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c8m11] Exception in async task async_call_c8m11___getstate__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c8m11___getstate__", file=stderr)
        fuzzer_async_tasks.append(async_call_c8m11___getstate__)

    try:
        res_c8m12 = callMethod("c8m12", instance_c8_popen, "__new__",
            373257,
            9,
            TypeFlipIterator(),
        verbose=True)
    except Exception as _argexc_c8m12:
        print("[c8m12] call skipped (argument build failed):", repr(_argexc_c8m12), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c8_popen, '__new__')
    except Exception as e_get_target_func:
        print(f"[c8m12] Failed to get attribute __new__ from instance_c8_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(LyingEq(), True, IndexBomb()), name='c8m12___new__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c8m12] Failed to create thread for __new__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c8m12___new__(target_func=target_func):
            print("Starting async task: async_call_c8m12___new__", file=stderr)
            time.sleep(0.000797) # Small delay
            try:
                target_func("", list[weird_classes['weird_list']] | weird_classes['weird_set'] | big_union, tricky_mappingproxy)
            except Exception as e_async_call:
                print(f"[c8m12] Exception in async task async_call_c8m12___new__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c8m12___new__", file=stderr)
        fuzzer_async_tasks.append(async_call_c8m12___new__)

    try:
        res_c8m13 = callMethod("c8m13", instance_c8_popen, "close",
        verbose=True)
    except Exception as _argexc_c8m13:
        print("[c8m13] call skipped (argument build failed):", repr(_argexc_c8m13), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c8_popen, 'close')
    except Exception as e_get_target_func:
        print(f"[c8m13] Failed to get attribute close from instance_c8_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c8m13_close')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c8m13] Failed to create thread for close: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c8m13_close(target_func=target_func):
            print("Starting async task: async_call_c8m13_close", file=stderr)
            time.sleep(0.000156) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c8m13] Exception in async task async_call_c8m13_close: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c8m13_close", file=stderr)
        fuzzer_async_tasks.append(async_call_c8m13_close)

    try:
        res_c8m14 = callMethod("c8m14", instance_c8_popen, "__init_subclass__",
            IndexBomb(),
        verbose=True)
    except Exception as _argexc_c8m14:
        print("[c8m14] call skipped (argument build failed):", repr(_argexc_c8m14), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c8_popen, '__init_subclass__')
    except Exception as e_get_target_func:
        print(f"[c8m14] Failed to get attribute __init_subclass__ from instance_c8_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("\u4CC1\u1DFF\uA05D\u08DA\u20D5\u5A1D\uB770\u89D9\u9522\u9BD5",), name='c8m14___init_subclass__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c8m14] Failed to create thread for __init_subclass__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c8m14___init_subclass__(target_func=target_func):
            print("Starting async task: async_call_c8m14___init_subclass__", file=stderr)
            time.sleep(0.000594) # Small delay
            try:
                target_func(float("nan"))
            except Exception as e_async_call:
                print(f"[c8m14] Exception in async task async_call_c8m14___init_subclass__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c8m14___init_subclass__", file=stderr)
        fuzzer_async_tasks.append(async_call_c8m14___init_subclass__)

    try:
        res_c8m15 = callMethod("c8m15", instance_c8_popen, "duplicate_for_child",
            r"fZ+\bxEAhcyad\d\DzR.Qg\WV+vV",
        verbose=True)
    except Exception as _argexc_c8m15:
        print("[c8m15] call skipped (argument build failed):", repr(_argexc_c8m15), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c8_popen, 'duplicate_for_child')
    except Exception as e_get_target_func:
        print(f"[c8m15] Failed to get attribute duplicate_for_child from instance_c8_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(r"^(?:a|aa)*$",), name='c8m15_duplicate_for_child')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c8m15] Failed to create thread for duplicate_for_child: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c8m15_duplicate_for_child(target_func=target_func):
            print("Starting async task: async_call_c8m15_duplicate_for_child", file=stderr)
            time.sleep(0.000485) # Small delay
            try:
                target_func('/tmp/fusil-fixtures/fusil_fixture.txt')
            except Exception as e_async_call:
                print(f"[c8m15] Exception in async task async_call_c8m15_duplicate_for_child: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c8m15_duplicate_for_child", file=stderr)
        fuzzer_async_tasks.append(async_call_c8m15_duplicate_for_child)

    print(f"--- Finished fuzzing instance: instance_c8_popen ---", file=stderr)

    del instance_c8_popen # Cleanup instance
    print("[c8] -explicit garbage collection for class instance-", file=stderr)
    collect()

print("[c9] Attempting to instantiate class: Popen", file=stderr)
instance_c9_popen = None # Initialize instance variable
try:
    instance_c9_popen = callFunc('c9_init', 'Popen',
        '/tmp/fusil-fixtures/fusil_fixture.bin',
      )
except Exception as e_instantiate:
    instance_c9_popen = None
    print("[c9] Failed to instantiate Popen: {e_instantiate.__class__.__name__} {e_instantiate}", file=stderr)
    instance_c9_popen = None

try:
    print(f"--- (Depth 0) Dispatching Fuzz for: {instance_c9_popen!r} (hint: Popen, prefix: c9_popen_ops) ---", file=stderr)
except Exception as e:
    print(f"--- (Depth 0) Error calling repr() prefix: c9_popen_ops) ---", file=stderr)
if instance_c9_popen is not None:
    if skip_trivial_type(instance_c9_popen):
        print(f'Skipping deep diving on instance_c9_popen {type(instance_c9_popen)}', file=stderr)
    try:
        print(f'Instance {instance_c9_popen!r} (actual type {type(instance_c9_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    except Exception as e:
        print(f'Error printing instance repr() { e } (actual type {type(instance_c9_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    if skip_trivial_type(instance_c9_popen):
        print(f'Skipping deep diving on instance_c9_popen {type(instance_c9_popen)}', file=stderr)
    else:
        print(f'Instance instance_c9_popen (type {type(instance_c9_popen).__name__}) has no specific fuzzer, doing generic calls.', file=stderr)
        c9_popen_ops_generic_methods = []
        try:
            for c9_popen_ops_generic_attr_name in dir(instance_c9_popen):
                if c9_popen_ops_generic_attr_name.startswith('_'): continue
                try:
                    c9_popen_ops_generic_attr_val = getattr(instance_c9_popen, c9_popen_ops_generic_attr_name)
                    if callable(c9_popen_ops_generic_attr_val) and c9_popen_ops_generic_attr_name not in _FUSIL_METHOD_BLACKLIST: c9_popen_ops_generic_methods.append((c9_popen_ops_generic_attr_name, c9_popen_ops_generic_attr_val))
                except Exception: pass
        except Exception: c9_popen_ops_generic_methods = [] # Failed to get methods
        if c9_popen_ops_generic_methods:
            print(f'Found {len(c9_popen_ops_generic_methods)} callable methods for generic fuzzing of instance_c9_popen', file=stderr)
            for _i_c9_popen_ops_generic in range(min(len(c9_popen_ops_generic_methods), 15)):
                c9_popen_ops_generic_method_name_to_call, c9_popen_ops_generic_method_obj_to_call = choice(c9_popen_ops_generic_methods)
                # Conceptual call to generic method fuzzer
                if c9_popen_ops_generic_method_name_to_call not in _FUSIL_METHOD_BLACKLIST: callMethod(f'c9_popen_ops_generic_gen{_i_c9_popen_ops_generic}', instance_c9_popen, c9_popen_ops_generic_method_name_to_call)

if instance_c9_popen is not None and instance_c9_popen is not SENTINEL_VALUE:
    print(f"--- Fuzzing instance: instance_c9_popen (type hint: Popen, prefix: c9m) ---", file=stderr)
    if skip_trivial_type(instance_c9_popen):
        print(f'Skipping deep diving on instance_c9_popen {type(instance_c9_popen)}', file=stderr)
    # General method fuzzing for instance_c9_popen
    try:
        res_c9m1 = callMethod("c9m1", instance_c9_popen, "__lt__",
            -51.5,
        verbose=True)
    except Exception as _argexc_c9m1:
        print("[c9m1] call skipped (argument build failed):", repr(_argexc_c9m1), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c9_popen, '__lt__')
    except Exception as e_get_target_func:
        print(f"[c9m1] Failed to get attribute __lt__ from instance_c9_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(IndexBomb(),), name='c9m1___lt__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c9m1] Failed to create thread for __lt__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c9m1___lt__(target_func=target_func):
            print("Starting async task: async_call_c9m1___lt__", file=stderr)
            time.sleep(0.000036) # Small delay
            try:
                target_func(DescriptorBomb())
            except Exception as e_async_call:
                print(f"[c9m1] Exception in async task async_call_c9m1___lt__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c9m1___lt__", file=stderr)
        fuzzer_async_tasks.append(async_call_c9m1___lt__)

    try:
        res_c9m2 = callMethod("c9m2", instance_c9_popen, "kill",
        verbose=True)
    except Exception as _argexc_c9m2:
        print("[c9m2] call skipped (argument build failed):", repr(_argexc_c9m2), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c9_popen, 'kill')
    except Exception as e_get_target_func:
        print(f"[c9m2] Failed to get attribute kill from instance_c9_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c9m2_kill')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c9m2] Failed to create thread for kill: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c9m2_kill(target_func=target_func):
            print("Starting async task: async_call_c9m2_kill", file=stderr)
            time.sleep(0.000864) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c9m2] Exception in async task async_call_c9m2_kill: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c9m2_kill", file=stderr)
        fuzzer_async_tasks.append(async_call_c9m2_kill)

    try:
        res_c9m3 = callMethod("c9m3", instance_c9_popen, "__gt__",
            r"d.a\s.lPnjj\wLcdsDP\sJNavtjFSbN",
        verbose=True)
    except Exception as _argexc_c9m3:
        print("[c9m3] call skipped (argument build failed):", repr(_argexc_c9m3), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c9_popen, '__gt__')
    except Exception as e_get_target_func:
        print(f"[c9m3] Failed to get attribute __gt__ from instance_c9_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(None,), name='c9m3___gt__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c9m3] Failed to create thread for __gt__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c9m3___gt__(target_func=target_func):
            print("Starting async task: async_call_c9m3___gt__", file=stderr)
            time.sleep(0.000583) # Small delay
            try:
                target_func("\u6CC7\u218E\u340E\uA05B\u0470\uF354\u7C26\u4DC5\u5E8F\u762D\u753E\u7FC5\u1336\uEB62")
            except Exception as e_async_call:
                print(f"[c9m3] Exception in async task async_call_c9m3___gt__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c9m3___gt__", file=stderr)
        fuzzer_async_tasks.append(async_call_c9m3___gt__)

    try:
        res_c9m4 = callMethod("c9m4", instance_c9_popen, "__getstate__",
        verbose=True)
    except Exception as _argexc_c9m4:
        print("[c9m4] call skipped (argument build failed):", repr(_argexc_c9m4), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c9_popen, '__getstate__')
    except Exception as e_get_target_func:
        print(f"[c9m4] Failed to get attribute __getstate__ from instance_c9_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c9m4___getstate__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c9m4] Failed to create thread for __getstate__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c9m4___getstate__(target_func=target_func):
            print("Starting async task: async_call_c9m4___getstate__", file=stderr)
            time.sleep(0.000374) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c9m4] Exception in async task async_call_c9m4___getstate__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c9m4___getstate__", file=stderr)
        fuzzer_async_tasks.append(async_call_c9m4___getstate__)

    try:
        res_c9m5 = callMethod("c9m5", instance_c9_popen, "__init__",
            b"",
        verbose=True)
    except Exception as _argexc_c9m5:
        print("[c9m5] call skipped (argument build failed):", repr(_argexc_c9m5), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c9_popen, '__init__')
    except Exception as e_get_target_func:
        print(f"[c9m5] Failed to get attribute __init__ from instance_c9_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("\xDE\x10xo$K\x1B",), name='c9m5___init__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c9m5] Failed to create thread for __init__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c9m5___init__(target_func=target_func):
            print("Starting async task: async_call_c9m5___init__", file=stderr)
            time.sleep(0.000531) # Small delay
            try:
                target_func(list[weird_classes['weird_list']] | weird_classes['weird_dict'] | big_union)
            except Exception as e_async_call:
                print(f"[c9m5] Exception in async task async_call_c9m5___init__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c9m5___init__", file=stderr)
        fuzzer_async_tasks.append(async_call_c9m5___init__)

    try:
        res_c9m6 = callMethod("c9m6", instance_c9_popen, "terminate",
        verbose=True)
    except Exception as _argexc_c9m6:
        print("[c9m6] call skipped (argument build failed):", repr(_argexc_c9m6), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c9_popen, 'terminate')
    except Exception as e_get_target_func:
        print(f"[c9m6] Failed to get attribute terminate from instance_c9_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c9m6_terminate')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c9m6] Failed to create thread for terminate: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c9m6_terminate(target_func=target_func):
            print("Starting async task: async_call_c9m6_terminate", file=stderr)
            time.sleep(0.000473) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c9m6] Exception in async task async_call_c9m6_terminate: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c9m6_terminate", file=stderr)
        fuzzer_async_tasks.append(async_call_c9m6_terminate)

    try:
        res_c9m7 = callMethod("c9m7", instance_c9_popen, "_send_signal",
            MutatingIterable(),
        verbose=True)
    except Exception as _argexc_c9m7:
        print("[c9m7] call skipped (argument build failed):", repr(_argexc_c9m7), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c9_popen, '_send_signal')
    except Exception as e_get_target_func:
        print(f"[c9m7] Failed to get attribute _send_signal from instance_c9_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(b"\xE8\x06\xBB\x82",), name='c9m7__send_signal')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c9m7] Failed to create thread for _send_signal: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c9m7__send_signal(target_func=target_func):
            print("Starting async task: async_call_c9m7__send_signal", file=stderr)
            time.sleep(0.000611) # Small delay
            try:
                target_func("\xBA!\x95\x93\x0F\xE3\xD7X\xDD\xA6y/\xF2<\xA4\x7Fj\xDE")
            except Exception as e_async_call:
                print(f"[c9m7] Exception in async task async_call_c9m7__send_signal: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c9m7__send_signal", file=stderr)
        fuzzer_async_tasks.append(async_call_c9m7__send_signal)

    try:
        res_c9m8 = callMethod("c9m8", instance_c9_popen, "_send_signal",
            True,
        verbose=True)
    except Exception as _argexc_c9m8:
        print("[c9m8] call skipped (argument build failed):", repr(_argexc_c9m8), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c9_popen, '_send_signal')
    except Exception as e_get_target_func:
        print(f"[c9m8] Failed to get attribute _send_signal from instance_c9_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(ReentrantClearDict(),), name='c9m8__send_signal')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c9m8] Failed to create thread for _send_signal: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c9m8__send_signal(target_func=target_func):
            print("Starting async task: async_call_c9m8__send_signal", file=stderr)
            time.sleep(0.000999) # Small delay
            try:
                target_func(Exception('fuzzer_generated_exception'))
            except Exception as e_async_call:
                print(f"[c9m8] Exception in async task async_call_c9m8__send_signal: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c9m8__send_signal", file=stderr)
        fuzzer_async_tasks.append(async_call_c9m8__send_signal)

    try:
        res_c9m9 = callMethod("c9m9", instance_c9_popen, "__gt__",
            HiddenNameType,
        verbose=True)
    except Exception as _argexc_c9m9:
        print("[c9m9] call skipped (argument build failed):", repr(_argexc_c9m9), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c9_popen, '__gt__')
    except Exception as e_get_target_func:
        print(f"[c9m9] Failed to get attribute __gt__ from instance_c9_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(tricky_capsule,), name='c9m9___gt__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c9m9] Failed to create thread for __gt__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c9m9___gt__(target_func=target_func):
            print("Starting async task: async_call_c9m9___gt__", file=stderr)
            time.sleep(0.000460) # Small delay
            try:
                target_func(list[weird_classes['weird_int']] | weird_classes['weird_bytearray'] | big_union)
            except Exception as e_async_call:
                print(f"[c9m9] Exception in async task async_call_c9m9___gt__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c9m9___gt__", file=stderr)
        fuzzer_async_tasks.append(async_call_c9m9___gt__)

    try:
        res_c9m10 = callMethod("c9m10", instance_c9_popen, "__eq__",
            list[weird_classes['weird_str']] | weird_classes['weird_frozenset'] | big_union,
        verbose=True)
    except Exception as _argexc_c9m10:
        print("[c9m10] call skipped (argument build failed):", repr(_argexc_c9m10), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c9_popen, '__eq__')
    except Exception as e_get_target_func:
        print(f"[c9m10] Failed to get attribute __eq__ from instance_c9_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("\uCFDE\uCB11\u502F\u4FFA\u59B3\uB84E\u95B0\u975B\u8808\u3422\u82C7\u682A\u2854\u81EC\u8F8D",), name='c9m10___eq__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c9m10] Failed to create thread for __eq__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c9m10___eq__(target_func=target_func):
            print("Starting async task: async_call_c9m10___eq__", file=stderr)
            time.sleep(0.000292) # Small delay
            try:
                target_func(LenBomb())
            except Exception as e_async_call:
                print(f"[c9m10] Exception in async task async_call_c9m10___eq__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c9m10___eq__", file=stderr)
        fuzzer_async_tasks.append(async_call_c9m10___eq__)

    try:
        res_c9m11 = callMethod("c9m11", instance_c9_popen, "__gt__",
            ReprBomb(),
        verbose=True)
    except Exception as _argexc_c9m11:
        print("[c9m11] call skipped (argument build failed):", repr(_argexc_c9m11), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c9_popen, '__gt__')
    except Exception as e_get_target_func:
        print(f"[c9m11] Failed to get attribute __gt__ from instance_c9_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(-sys.float_info.epsilon,), name='c9m11___gt__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c9m11] Failed to create thread for __gt__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c9m11___gt__(target_func=target_func):
            print("Starting async task: async_call_c9m11___gt__", file=stderr)
            time.sleep(0.000210) # Small delay
            try:
                target_func(tuple[weird_classes['weird_Queue']])
            except Exception as e_async_call:
                print(f"[c9m11] Exception in async task async_call_c9m11___gt__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c9m11___gt__", file=stderr)
        fuzzer_async_tasks.append(async_call_c9m11___gt__)

    try:
        res_c9m12 = callMethod("c9m12", instance_c9_popen, "__init_subclass__",
            Exception('fuzzer_generated_exception'),
            None,
        verbose=True)
    except Exception as _argexc_c9m12:
        print("[c9m12] call skipped (argument build failed):", repr(_argexc_c9m12), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c9_popen, '__init_subclass__')
    except Exception as e_get_target_func:
        print(f"[c9m12] Failed to get attribute __init_subclass__ from instance_c9_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("\x91B", "\x00"), name='c9m12___init_subclass__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c9m12] Failed to create thread for __init_subclass__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c9m12___init_subclass__(target_func=target_func):
            print("Starting async task: async_call_c9m12___init_subclass__", file=stderr)
            time.sleep(0.000119) # Small delay
            try:
                target_func(RaisingInstanceCheckType, errback)
            except Exception as e_async_call:
                print(f"[c9m12] Exception in async task async_call_c9m12___init_subclass__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c9m12___init_subclass__", file=stderr)
        fuzzer_async_tasks.append(async_call_c9m12___init_subclass__)

    try:
        res_c9m13 = callMethod("c9m13", instance_c9_popen, "__ge__",
            HashBomb(),
        verbose=True)
    except Exception as _argexc_c9m13:
        print("[c9m13] call skipped (argument build failed):", repr(_argexc_c9m13), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c9_popen, '__ge__')
    except Exception as e_get_target_func:
        print(f"[c9m13] Failed to get attribute __ge__ from instance_c9_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(tricky_cell,), name='c9m13___ge__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c9m13] Failed to create thread for __ge__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c9m13___ge__(target_func=target_func):
            print("Starting async task: async_call_c9m13___ge__", file=stderr)
            time.sleep(0.000060) # Small delay
            try:
                target_func(errback)
            except Exception as e_async_call:
                print(f"[c9m13] Exception in async task async_call_c9m13___ge__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c9m13___ge__", file=stderr)
        fuzzer_async_tasks.append(async_call_c9m13___ge__)

    try:
        res_c9m14 = callMethod("c9m14", instance_c9_popen, "__gt__",
            b"\xF0\x81\xAC\xF8\x7B\xAB\x5A\x34\xDE\x00\x04\x7C\x6B\x91\x02\x2C\x8F\x6E\x4F",
        verbose=True)
    except Exception as _argexc_c9m14:
        print("[c9m14] call skipped (argument build failed):", repr(_argexc_c9m14), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c9_popen, '__gt__')
    except Exception as e_get_target_func:
        print(f"[c9m14] Failed to get attribute __gt__ from instance_c9_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("\x00",), name='c9m14___gt__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c9m14] Failed to create thread for __gt__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c9m14___gt__(target_func=target_func):
            print("Starting async task: async_call_c9m14___gt__", file=stderr)
            time.sleep(0.000430) # Small delay
            try:
                target_func(-6187814277)
            except Exception as e_async_call:
                print(f"[c9m14] Exception in async task async_call_c9m14___gt__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c9m14___gt__", file=stderr)
        fuzzer_async_tasks.append(async_call_c9m14___gt__)

    try:
        res_c9m15 = callMethod("c9m15", instance_c9_popen, "__format__",
            MagicMock(),
        verbose=True)
    except Exception as _argexc_c9m15:
        print("[c9m15] call skipped (argument build failed):", repr(_argexc_c9m15), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c9_popen, '__format__')
    except Exception as e_get_target_func:
        print(f"[c9m15] Failed to get attribute __format__ from instance_c9_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(1.9224,), name='c9m15___format__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c9m15] Failed to create thread for __format__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c9m15___format__(target_func=target_func):
            print("Starting async task: async_call_c9m15___format__", file=stderr)
            time.sleep(0.000201) # Small delay
            try:
                target_func(ShiftyEq())
            except Exception as e_async_call:
                print(f"[c9m15] Exception in async task async_call_c9m15___format__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c9m15___format__", file=stderr)
        fuzzer_async_tasks.append(async_call_c9m15___format__)

    print(f"--- Finished fuzzing instance: instance_c9_popen ---", file=stderr)

    del instance_c9_popen # Cleanup instance
    print("[c9] -explicit garbage collection for class instance-", file=stderr)
    collect()

print("[c10] Attempting to instantiate class: Popen", file=stderr)
instance_c10_popen = None # Initialize instance variable
try:
    instance_c10_popen = callFunc('c10_init', 'Popen',
        None,
      )
except Exception as e_instantiate:
    instance_c10_popen = None
    print("[c10] Failed to instantiate Popen: {e_instantiate.__class__.__name__} {e_instantiate}", file=stderr)
    instance_c10_popen = None

try:
    print(f"--- (Depth 0) Dispatching Fuzz for: {instance_c10_popen!r} (hint: Popen, prefix: c10_popen_ops) ---", file=stderr)
except Exception as e:
    print(f"--- (Depth 0) Error calling repr() prefix: c10_popen_ops) ---", file=stderr)
if instance_c10_popen is not None:
    if skip_trivial_type(instance_c10_popen):
        print(f'Skipping deep diving on instance_c10_popen {type(instance_c10_popen)}', file=stderr)
    try:
        print(f'Instance {instance_c10_popen!r} (actual type {type(instance_c10_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    except Exception as e:
        print(f'Error printing instance repr() { e } (actual type {type(instance_c10_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    if skip_trivial_type(instance_c10_popen):
        print(f'Skipping deep diving on instance_c10_popen {type(instance_c10_popen)}', file=stderr)
    else:
        print(f'Instance instance_c10_popen (type {type(instance_c10_popen).__name__}) has no specific fuzzer, doing generic calls.', file=stderr)
        c10_popen_ops_generic_methods = []
        try:
            for c10_popen_ops_generic_attr_name in dir(instance_c10_popen):
                if c10_popen_ops_generic_attr_name.startswith('_'): continue
                try:
                    c10_popen_ops_generic_attr_val = getattr(instance_c10_popen, c10_popen_ops_generic_attr_name)
                    if callable(c10_popen_ops_generic_attr_val) and c10_popen_ops_generic_attr_name not in _FUSIL_METHOD_BLACKLIST: c10_popen_ops_generic_methods.append((c10_popen_ops_generic_attr_name, c10_popen_ops_generic_attr_val))
                except Exception: pass
        except Exception: c10_popen_ops_generic_methods = [] # Failed to get methods
        if c10_popen_ops_generic_methods:
            print(f'Found {len(c10_popen_ops_generic_methods)} callable methods for generic fuzzing of instance_c10_popen', file=stderr)
            for _i_c10_popen_ops_generic in range(min(len(c10_popen_ops_generic_methods), 15)):
                c10_popen_ops_generic_method_name_to_call, c10_popen_ops_generic_method_obj_to_call = choice(c10_popen_ops_generic_methods)
                # Conceptual call to generic method fuzzer
                if c10_popen_ops_generic_method_name_to_call not in _FUSIL_METHOD_BLACKLIST: callMethod(f'c10_popen_ops_generic_gen{_i_c10_popen_ops_generic}', instance_c10_popen, c10_popen_ops_generic_method_name_to_call)

if instance_c10_popen is not None and instance_c10_popen is not SENTINEL_VALUE:
    print(f"--- Fuzzing instance: instance_c10_popen (type hint: Popen, prefix: c10m) ---", file=stderr)
    if skip_trivial_type(instance_c10_popen):
        print(f'Skipping deep diving on instance_c10_popen {type(instance_c10_popen)}', file=stderr)
    # General method fuzzing for instance_c10_popen
    try:
        res_c10m1 = callMethod("c10m1", instance_c10_popen, "__hash__",
        verbose=True)
    except Exception as _argexc_c10m1:
        print("[c10m1] call skipped (argument build failed):", repr(_argexc_c10m1), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c10_popen, '__hash__')
    except Exception as e_get_target_func:
        print(f"[c10m1] Failed to get attribute __hash__ from instance_c10_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c10m1___hash__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c10m1] Failed to create thread for __hash__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c10m1___hash__(target_func=target_func):
            print("Starting async task: async_call_c10m1___hash__", file=stderr)
            time.sleep(0.000400) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c10m1] Exception in async task async_call_c10m1___hash__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c10m1___hash__", file=stderr)
        fuzzer_async_tasks.append(async_call_c10m1___hash__)

    try:
        res_c10m2 = callMethod("c10m2", instance_c10_popen, "__reduce_ex__",
            True,
        verbose=True)
    except Exception as _argexc_c10m2:
        print("[c10m2] call skipped (argument build failed):", repr(_argexc_c10m2), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c10_popen, '__reduce_ex__')
    except Exception as e_get_target_func:
        print(f"[c10m2] Failed to get attribute __reduce_ex__ from instance_c10_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(errback,), name='c10m2___reduce_ex__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c10m2] Failed to create thread for __reduce_ex__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c10m2___reduce_ex__(target_func=target_func):
            print("Starting async task: async_call_c10m2___reduce_ex__", file=stderr)
            time.sleep(0.000354) # Small delay
            try:
                target_func(inspect)
            except Exception as e_async_call:
                print(f"[c10m2] Exception in async task async_call_c10m2___reduce_ex__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c10m2___reduce_ex__", file=stderr)
        fuzzer_async_tasks.append(async_call_c10m2___reduce_ex__)

    try:
        res_c10m3 = callMethod("c10m3", instance_c10_popen, "__dir__",
        verbose=True)
    except Exception as _argexc_c10m3:
        print("[c10m3] call skipped (argument build failed):", repr(_argexc_c10m3), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c10_popen, '__dir__')
    except Exception as e_get_target_func:
        print(f"[c10m3] Failed to get attribute __dir__ from instance_c10_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c10m3___dir__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c10m3] Failed to create thread for __dir__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c10m3___dir__(target_func=target_func):
            print("Starting async task: async_call_c10m3___dir__", file=stderr)
            time.sleep(0.000732) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c10m3] Exception in async task async_call_c10m3___dir__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c10m3___dir__", file=stderr)
        fuzzer_async_tasks.append(async_call_c10m3___dir__)

    try:
        res_c10m4 = callMethod("c10m4", instance_c10_popen, "_launch",
            "\xC6\xF2\x87\x0E",
        verbose=True)
    except Exception as _argexc_c10m4:
        print("[c10m4] call skipped (argument build failed):", repr(_argexc_c10m4), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c10_popen, '_launch')
    except Exception as e_get_target_func:
        print(f"[c10m4] Failed to get attribute _launch from instance_c10_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(LyingEq(),), name='c10m4__launch')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c10m4] Failed to create thread for _launch: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c10m4__launch(target_func=target_func):
            print("Starting async task: async_call_c10m4__launch", file=stderr)
            time.sleep(0.000524) # Small delay
            try:
                target_func(weird_classes['weird_str'])
            except Exception as e_async_call:
                print(f"[c10m4] Exception in async task async_call_c10m4__launch: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c10m4__launch", file=stderr)
        fuzzer_async_tasks.append(async_call_c10m4__launch)

    try:
        res_c10m5 = callMethod("c10m5", instance_c10_popen, "terminate",
        verbose=True)
    except Exception as _argexc_c10m5:
        print("[c10m5] call skipped (argument build failed):", repr(_argexc_c10m5), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c10_popen, 'terminate')
    except Exception as e_get_target_func:
        print(f"[c10m5] Failed to get attribute terminate from instance_c10_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c10m5_terminate')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c10m5] Failed to create thread for terminate: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c10m5_terminate(target_func=target_func):
            print("Starting async task: async_call_c10m5_terminate", file=stderr)
            time.sleep(0.000707) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c10m5] Exception in async task async_call_c10m5_terminate: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c10m5_terminate", file=stderr)
        fuzzer_async_tasks.append(async_call_c10m5_terminate)

    try:
        res_c10m6 = callMethod("c10m6", instance_c10_popen, "__gt__",
            "^\x0F\x89\x96\xE1\xB7\xA0\x0CV/\xF517N\xED",
        verbose=True)
    except Exception as _argexc_c10m6:
        print("[c10m6] call skipped (argument build failed):", repr(_argexc_c10m6), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c10_popen, '__gt__')
    except Exception as e_get_target_func:
        print(f"[c10m6] Failed to get attribute __gt__ from instance_c10_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(RaisingInstanceCheckType,), name='c10m6___gt__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c10m6] Failed to create thread for __gt__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c10m6___gt__(target_func=target_func):
            print("Starting async task: async_call_c10m6___gt__", file=stderr)
            time.sleep(0.000230) # Small delay
            try:
                target_func(ShiftyEq())
            except Exception as e_async_call:
                print(f"[c10m6] Exception in async task async_call_c10m6___gt__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c10m6___gt__", file=stderr)
        fuzzer_async_tasks.append(async_call_c10m6___gt__)

    try:
        res_c10m7 = callMethod("c10m7", instance_c10_popen, "__new__",
            "\x0E\xD9\xFBY\xF1",
            None,
            b"\xBC\x49\x86\x1C\x18\xEB\x93\x36\x43\xE8\x5D\xF5\x87\xDD\xEC\x5A",
        verbose=True)
    except Exception as _argexc_c10m7:
        print("[c10m7] call skipped (argument build failed):", repr(_argexc_c10m7), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c10_popen, '__new__')
    except Exception as e_get_target_func:
        print(f"[c10m7] Failed to get attribute __new__ from instance_c10_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("\x00", EqBomb(), LenBomb()), name='c10m7___new__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c10m7] Failed to create thread for __new__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c10m7___new__(target_func=target_func):
            print("Starting async task: async_call_c10m7___new__", file=stderr)
            time.sleep(0.000183) # Small delay
            try:
                target_func(float("-inf"), "\udbff\udfff", 89.4268)
            except Exception as e_async_call:
                print(f"[c10m7] Exception in async task async_call_c10m7___new__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c10m7___new__", file=stderr)
        fuzzer_async_tasks.append(async_call_c10m7___new__)

    try:
        res_c10m8 = callMethod("c10m8", instance_c10_popen, "__str__",
        verbose=True)
    except Exception as _argexc_c10m8:
        print("[c10m8] call skipped (argument build failed):", repr(_argexc_c10m8), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c10_popen, '__str__')
    except Exception as e_get_target_func:
        print(f"[c10m8] Failed to get attribute __str__ from instance_c10_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c10m8___str__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c10m8] Failed to create thread for __str__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c10m8___str__(target_func=target_func):
            print("Starting async task: async_call_c10m8___str__", file=stderr)
            time.sleep(0.000260) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c10m8] Exception in async task async_call_c10m8___str__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c10m8___str__", file=stderr)
        fuzzer_async_tasks.append(async_call_c10m8___str__)

    try:
        res_c10m9 = callMethod("c10m9", instance_c10_popen, "__init__",
            -3,
        verbose=True)
    except Exception as _argexc_c10m9:
        print("[c10m9] call skipped (argument build failed):", repr(_argexc_c10m9), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c10_popen, '__init__')
    except Exception as e_get_target_func:
        print(f"[c10m9] Failed to get attribute __init__ from instance_c10_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(list[weird_classes['weird_set']],), name='c10m9___init__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c10m9] Failed to create thread for __init__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c10m9___init__(target_func=target_func):
            print("Starting async task: async_call_c10m9___init__", file=stderr)
            time.sleep(0.000523) # Small delay
            try:
                target_func(liar2)
            except Exception as e_async_call:
                print(f"[c10m9] Exception in async task async_call_c10m9___init__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c10m9___init__", file=stderr)
        fuzzer_async_tasks.append(async_call_c10m9___init__)

    try:
        res_c10m10 = callMethod("c10m10", instance_c10_popen, "__reduce__",
        verbose=True)
    except Exception as _argexc_c10m10:
        print("[c10m10] call skipped (argument build failed):", repr(_argexc_c10m10), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c10_popen, '__reduce__')
    except Exception as e_get_target_func:
        print(f"[c10m10] Failed to get attribute __reduce__ from instance_c10_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c10m10___reduce__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c10m10] Failed to create thread for __reduce__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c10m10___reduce__(target_func=target_func):
            print("Starting async task: async_call_c10m10___reduce__", file=stderr)
            time.sleep(0.000620) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c10m10] Exception in async task async_call_c10m10___reduce__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c10m10___reduce__", file=stderr)
        fuzzer_async_tasks.append(async_call_c10m10___reduce__)

    try:
        res_c10m11 = callMethod("c10m11", instance_c10_popen, "__reduce__",
            None,
        verbose=True)
    except Exception as _argexc_c10m11:
        print("[c10m11] call skipped (argument build failed):", repr(_argexc_c10m11), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c10_popen, '__reduce__')
    except Exception as e_get_target_func:
        print(f"[c10m11] Failed to get attribute __reduce__ from instance_c10_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(EqBomb(),), name='c10m11___reduce__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c10m11] Failed to create thread for __reduce__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c10m11___reduce__(target_func=target_func):
            print("Starting async task: async_call_c10m11___reduce__", file=stderr)
            time.sleep(0.000566) # Small delay
            try:
                target_func(False)
            except Exception as e_async_call:
                print(f"[c10m11] Exception in async task async_call_c10m11___reduce__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c10m11___reduce__", file=stderr)
        fuzzer_async_tasks.append(async_call_c10m11___reduce__)

    try:
        res_c10m12 = callMethod("c10m12", instance_c10_popen, "__subclasshook__",
            "\udbff\udfff",
        verbose=True)
    except Exception as _argexc_c10m12:
        print("[c10m12] call skipped (argument build failed):", repr(_argexc_c10m12), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c10_popen, '__subclasshook__')
    except Exception as e_get_target_func:
        print(f"[c10m12] Failed to get attribute __subclasshook__ from instance_c10_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(ReprBomb(),), name='c10m12___subclasshook__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c10m12] Failed to create thread for __subclasshook__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c10m12___subclasshook__(target_func=target_func):
            print("Starting async task: async_call_c10m12___subclasshook__", file=stderr)
            time.sleep(0.000472) # Small delay
            try:
                target_func('/tmp/fusil-fixtures/fusil_fixture.txt')
            except Exception as e_async_call:
                print(f"[c10m12] Exception in async task async_call_c10m12___subclasshook__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c10m12___subclasshook__", file=stderr)
        fuzzer_async_tasks.append(async_call_c10m12___subclasshook__)

    try:
        res_c10m13 = callMethod("c10m13", instance_c10_popen, "poll",
            HiddenNameType,
        verbose=True)
    except Exception as _argexc_c10m13:
        print("[c10m13] call skipped (argument build failed):", repr(_argexc_c10m13), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c10_popen, 'poll')
    except Exception as e_get_target_func:
        print(f"[c10m13] Failed to get attribute poll from instance_c10_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("\uC759\u75AF\u167F\u59B1\u6114\u7D6A",), name='c10m13_poll')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c10m13] Failed to create thread for poll: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c10m13_poll(target_func=target_func):
            print("Starting async task: async_call_c10m13_poll", file=stderr)
            time.sleep(0.000043) # Small delay
            try:
                target_func(HiddenNameType)
            except Exception as e_async_call:
                print(f"[c10m13] Exception in async task async_call_c10m13_poll: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c10m13_poll", file=stderr)
        fuzzer_async_tasks.append(async_call_c10m13_poll)

    try:
        res_c10m14 = callMethod("c10m14", instance_c10_popen, "__str__",
        verbose=True)
    except Exception as _argexc_c10m14:
        print("[c10m14] call skipped (argument build failed):", repr(_argexc_c10m14), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c10_popen, '__str__')
    except Exception as e_get_target_func:
        print(f"[c10m14] Failed to get attribute __str__ from instance_c10_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c10m14___str__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c10m14] Failed to create thread for __str__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c10m14___str__(target_func=target_func):
            print("Starting async task: async_call_c10m14___str__", file=stderr)
            time.sleep(0.000067) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c10m14] Exception in async task async_call_c10m14___str__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c10m14___str__", file=stderr)
        fuzzer_async_tasks.append(async_call_c10m14___str__)

    try:
        res_c10m15 = callMethod("c10m15", instance_c10_popen, "duplicate_for_child",
            RaisingInstanceCheckType,
        verbose=True)
    except Exception as _argexc_c10m15:
        print("[c10m15] call skipped (argument build failed):", repr(_argexc_c10m15), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c10_popen, 'duplicate_for_child')
    except Exception as e_get_target_func:
        print(f"[c10m15] Failed to get attribute duplicate_for_child from instance_c10_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(errback,), name='c10m15_duplicate_for_child')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c10m15] Failed to create thread for duplicate_for_child: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c10m15_duplicate_for_child(target_func=target_func):
            print("Starting async task: async_call_c10m15_duplicate_for_child", file=stderr)
            time.sleep(0.000337) # Small delay
            try:
                target_func("`\x85\xD6\xD8\x14\xF7?")
            except Exception as e_async_call:
                print(f"[c10m15] Exception in async task async_call_c10m15_duplicate_for_child: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c10m15_duplicate_for_child", file=stderr)
        fuzzer_async_tasks.append(async_call_c10m15_duplicate_for_child)

    print(f"--- Finished fuzzing instance: instance_c10_popen ---", file=stderr)

    del instance_c10_popen # Cleanup instance
    print("[c10] -explicit garbage collection for class instance-", file=stderr)
    collect()

print("[c11] Attempting to instantiate class: Popen", file=stderr)
instance_c11_popen = None # Initialize instance variable
try:
    instance_c11_popen = callFunc('c11_init', 'Popen',
        Exception('fuzzer_generated_exception'),
      )
except Exception as e_instantiate:
    instance_c11_popen = None
    print("[c11] Failed to instantiate Popen: {e_instantiate.__class__.__name__} {e_instantiate}", file=stderr)
    instance_c11_popen = None

try:
    print(f"--- (Depth 0) Dispatching Fuzz for: {instance_c11_popen!r} (hint: Popen, prefix: c11_popen_ops) ---", file=stderr)
except Exception as e:
    print(f"--- (Depth 0) Error calling repr() prefix: c11_popen_ops) ---", file=stderr)
if instance_c11_popen is not None:
    if skip_trivial_type(instance_c11_popen):
        print(f'Skipping deep diving on instance_c11_popen {type(instance_c11_popen)}', file=stderr)
    try:
        print(f'Instance {instance_c11_popen!r} (actual type {type(instance_c11_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    except Exception as e:
        print(f'Error printing instance repr() { e } (actual type {type(instance_c11_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    if skip_trivial_type(instance_c11_popen):
        print(f'Skipping deep diving on instance_c11_popen {type(instance_c11_popen)}', file=stderr)
    else:
        print(f'Instance instance_c11_popen (type {type(instance_c11_popen).__name__}) has no specific fuzzer, doing generic calls.', file=stderr)
        c11_popen_ops_generic_methods = []
        try:
            for c11_popen_ops_generic_attr_name in dir(instance_c11_popen):
                if c11_popen_ops_generic_attr_name.startswith('_'): continue
                try:
                    c11_popen_ops_generic_attr_val = getattr(instance_c11_popen, c11_popen_ops_generic_attr_name)
                    if callable(c11_popen_ops_generic_attr_val) and c11_popen_ops_generic_attr_name not in _FUSIL_METHOD_BLACKLIST: c11_popen_ops_generic_methods.append((c11_popen_ops_generic_attr_name, c11_popen_ops_generic_attr_val))
                except Exception: pass
        except Exception: c11_popen_ops_generic_methods = [] # Failed to get methods
        if c11_popen_ops_generic_methods:
            print(f'Found {len(c11_popen_ops_generic_methods)} callable methods for generic fuzzing of instance_c11_popen', file=stderr)
            for _i_c11_popen_ops_generic in range(min(len(c11_popen_ops_generic_methods), 15)):
                c11_popen_ops_generic_method_name_to_call, c11_popen_ops_generic_method_obj_to_call = choice(c11_popen_ops_generic_methods)
                # Conceptual call to generic method fuzzer
                if c11_popen_ops_generic_method_name_to_call not in _FUSIL_METHOD_BLACKLIST: callMethod(f'c11_popen_ops_generic_gen{_i_c11_popen_ops_generic}', instance_c11_popen, c11_popen_ops_generic_method_name_to_call)

if instance_c11_popen is not None and instance_c11_popen is not SENTINEL_VALUE:
    print(f"--- Fuzzing instance: instance_c11_popen (type hint: Popen, prefix: c11m) ---", file=stderr)
    if skip_trivial_type(instance_c11_popen):
        print(f'Skipping deep diving on instance_c11_popen {type(instance_c11_popen)}', file=stderr)
    # General method fuzzing for instance_c11_popen
    try:
        res_c11m1 = callMethod("c11m1", instance_c11_popen, "kill",
        verbose=True)
    except Exception as _argexc_c11m1:
        print("[c11m1] call skipped (argument build failed):", repr(_argexc_c11m1), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c11_popen, 'kill')
    except Exception as e_get_target_func:
        print(f"[c11m1] Failed to get attribute kill from instance_c11_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c11m1_kill')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c11m1] Failed to create thread for kill: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c11m1_kill(target_func=target_func):
            print("Starting async task: async_call_c11m1_kill", file=stderr)
            time.sleep(0.000106) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c11m1] Exception in async task async_call_c11m1_kill: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c11m1_kill", file=stderr)
        fuzzer_async_tasks.append(async_call_c11m1_kill)

    try:
        res_c11m2 = callMethod("c11m2", instance_c11_popen, "__dir__",
        verbose=True)
    except Exception as _argexc_c11m2:
        print("[c11m2] call skipped (argument build failed):", repr(_argexc_c11m2), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c11_popen, '__dir__')
    except Exception as e_get_target_func:
        print(f"[c11m2] Failed to get attribute __dir__ from instance_c11_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c11m2___dir__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c11m2] Failed to create thread for __dir__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c11m2___dir__(target_func=target_func):
            print("Starting async task: async_call_c11m2___dir__", file=stderr)
            time.sleep(0.000561) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c11m2] Exception in async task async_call_c11m2___dir__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c11m2___dir__", file=stderr)
        fuzzer_async_tasks.append(async_call_c11m2___dir__)

    try:
        res_c11m3 = callMethod("c11m3", instance_c11_popen, "__gt__",
            memoryview(bytearray(b"abc\xe9\xff")),
        verbose=True)
    except Exception as _argexc_c11m3:
        print("[c11m3] call skipped (argument build failed):", repr(_argexc_c11m3), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c11_popen, '__gt__')
    except Exception as e_get_target_func:
        print(f"[c11m3] Failed to get attribute __gt__ from instance_c11_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(list[weird_classes['weird_set']] | weird_classes['weird_frozenset'] | big_union,), name='c11m3___gt__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c11m3] Failed to create thread for __gt__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c11m3___gt__(target_func=target_func):
            print("Starting async task: async_call_c11m3___gt__", file=stderr)
            time.sleep(0.000405) # Small delay
            try:
                target_func('/tmp/fusil-fixtures/fusil_fixture.bin')
            except Exception as e_async_call:
                print(f"[c11m3] Exception in async task async_call_c11m3___gt__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c11m3___gt__", file=stderr)
        fuzzer_async_tasks.append(async_call_c11m3___gt__)

    try:
        res_c11m4 = callMethod("c11m4", instance_c11_popen, "__getstate__",
        verbose=True)
    except Exception as _argexc_c11m4:
        print("[c11m4] call skipped (argument build failed):", repr(_argexc_c11m4), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c11_popen, '__getstate__')
    except Exception as e_get_target_func:
        print(f"[c11m4] Failed to get attribute __getstate__ from instance_c11_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c11m4___getstate__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c11m4] Failed to create thread for __getstate__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c11m4___getstate__(target_func=target_func):
            print("Starting async task: async_call_c11m4___getstate__", file=stderr)
            time.sleep(0.000629) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c11m4] Exception in async task async_call_c11m4___getstate__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c11m4___getstate__", file=stderr)
        fuzzer_async_tasks.append(async_call_c11m4___getstate__)

    try:
        res_c11m5 = callMethod("c11m5", instance_c11_popen, "duplicate_for_child",
            LyingInstanceCheckType,
        verbose=True)
    except Exception as _argexc_c11m5:
        print("[c11m5] call skipped (argument build failed):", repr(_argexc_c11m5), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c11_popen, 'duplicate_for_child')
    except Exception as e_get_target_func:
        print(f"[c11m5] Failed to get attribute duplicate_for_child from instance_c11_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(dict[weird_classes['weird_Queue']] | weird_classes['weird_OrderedDict'] | big_union,), name='c11m5_duplicate_for_child')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c11m5] Failed to create thread for duplicate_for_child: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c11m5_duplicate_for_child(target_func=target_func):
            print("Starting async task: async_call_c11m5_duplicate_for_child", file=stderr)
            time.sleep(0.000673) # Small delay
            try:
                target_func(960.643)
            except Exception as e_async_call:
                print(f"[c11m5] Exception in async task async_call_c11m5_duplicate_for_child: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c11m5_duplicate_for_child", file=stderr)
        fuzzer_async_tasks.append(async_call_c11m5_duplicate_for_child)

    try:
        res_c11m6 = callMethod("c11m6", instance_c11_popen, "duplicate_for_child",
            False,
        verbose=True)
    except Exception as _argexc_c11m6:
        print("[c11m6] call skipped (argument build failed):", repr(_argexc_c11m6), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c11_popen, 'duplicate_for_child')
    except Exception as e_get_target_func:
        print(f"[c11m6] Failed to get attribute duplicate_for_child from instance_c11_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(ReentrantClearList(),), name='c11m6_duplicate_for_child')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c11m6] Failed to create thread for duplicate_for_child: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c11m6_duplicate_for_child(target_func=target_func):
            print("Starting async task: async_call_c11m6_duplicate_for_child", file=stderr)
            time.sleep(0.000247) # Small delay
            try:
                target_func(bytearray(b"abc\xe9\xff"))
            except Exception as e_async_call:
                print(f"[c11m6] Exception in async task async_call_c11m6_duplicate_for_child: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c11m6_duplicate_for_child", file=stderr)
        fuzzer_async_tasks.append(async_call_c11m6_duplicate_for_child)

    try:
        res_c11m7 = callMethod("c11m7", instance_c11_popen, "_launch",
            GrowingLen(),
        verbose=True)
    except Exception as _argexc_c11m7:
        print("[c11m7] call skipped (argument build failed):", repr(_argexc_c11m7), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c11_popen, '_launch')
    except Exception as e_get_target_func:
        print(f"[c11m7] Failed to get attribute _launch from instance_c11_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(weird_classes['weird_deque'],), name='c11m7__launch')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c11m7] Failed to create thread for _launch: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c11m7__launch(target_func=target_func):
            print("Starting async task: async_call_c11m7__launch", file=stderr)
            time.sleep(0.000899) # Small delay
            try:
                target_func(errback)
            except Exception as e_async_call:
                print(f"[c11m7] Exception in async task async_call_c11m7__launch: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c11m7__launch", file=stderr)
        fuzzer_async_tasks.append(async_call_c11m7__launch)

    try:
        res_c11m8 = callMethod("c11m8", instance_c11_popen, "__new__",
            -4,
            '/tmp/fusil-fixtures/fusil_fixture.txt',
            EqBomb(),
        verbose=True)
    except Exception as _argexc_c11m8:
        print("[c11m8] call skipped (argument build failed):", repr(_argexc_c11m8), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c11_popen, '__new__')
    except Exception as e_get_target_func:
        print(f"[c11m8] Failed to get attribute __new__ from instance_c11_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("\xED\x8BEn\xAD\xEF", "\u3751\uEDB1\u4574\uEFE0\u05F2\u48EC\u73F9\uDDE5\uCCE8\u429A", list[weird_classes['weird_list']]), name='c11m8___new__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c11m8] Failed to create thread for __new__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c11m8___new__(target_func=target_func):
            print("Starting async task: async_call_c11m8___new__", file=stderr)
            time.sleep(0.000002) # Small delay
            try:
                target_func(complex(sys.maxsize, sys.maxsize), [[]], 18)
            except Exception as e_async_call:
                print(f"[c11m8] Exception in async task async_call_c11m8___new__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c11m8___new__", file=stderr)
        fuzzer_async_tasks.append(async_call_c11m8___new__)

    try:
        res_c11m9 = callMethod("c11m9", instance_c11_popen, "__new__",
            r"Ly?.PM\B\de.IKwG\DPmO.to.\AM.m\WOc\w..Xl.opI",
        verbose=True)
    except Exception as _argexc_c11m9:
        print("[c11m9] call skipped (argument build failed):", repr(_argexc_c11m9), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c11_popen, '__new__')
    except Exception as e_get_target_func:
        print(f"[c11m9] Failed to get attribute __new__ from instance_c11_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("\uDC80",), name='c11m9___new__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c11m9] Failed to create thread for __new__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c11m9___new__(target_func=target_func):
            print("Starting async task: async_call_c11m9___new__", file=stderr)
            time.sleep(0.000404) # Small delay
            try:
                target_func(bytearray(b"abc\xe9\xff"))
            except Exception as e_async_call:
                print(f"[c11m9] Exception in async task async_call_c11m9___new__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c11m9___new__", file=stderr)
        fuzzer_async_tasks.append(async_call_c11m9___new__)

    try:
        res_c11m10 = callMethod("c11m10", instance_c11_popen, "poll",
            EqBomb(),
        verbose=True)
    except Exception as _argexc_c11m10:
        print("[c11m10] call skipped (argument build failed):", repr(_argexc_c11m10), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c11_popen, 'poll')
    except Exception as e_get_target_func:
        print(f"[c11m10] Failed to get attribute poll from instance_c11_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(LyingInplace(),), name='c11m10_poll')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c11m10] Failed to create thread for poll: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c11m10_poll(target_func=target_func):
            print("Starting async task: async_call_c11m10_poll", file=stderr)
            time.sleep(0.000478) # Small delay
            try:
                target_func(-1j)
            except Exception as e_async_call:
                print(f"[c11m10] Exception in async task async_call_c11m10_poll: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c11m10_poll", file=stderr)
        fuzzer_async_tasks.append(async_call_c11m10_poll)

    try:
        res_c11m11 = callMethod("c11m11", instance_c11_popen, "__repr__",
        verbose=True)
    except Exception as _argexc_c11m11:
        print("[c11m11] call skipped (argument build failed):", repr(_argexc_c11m11), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c11_popen, '__repr__')
    except Exception as e_get_target_func:
        print(f"[c11m11] Failed to get attribute __repr__ from instance_c11_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c11m11___repr__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c11m11] Failed to create thread for __repr__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c11m11___repr__(target_func=target_func):
            print("Starting async task: async_call_c11m11___repr__", file=stderr)
            time.sleep(0.000886) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c11m11] Exception in async task async_call_c11m11___repr__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c11m11___repr__", file=stderr)
        fuzzer_async_tasks.append(async_call_c11m11___repr__)

    try:
        res_c11m12 = callMethod("c11m12", instance_c11_popen, "_send_signal",
            MutatingIterable(),
        verbose=True)
    except Exception as _argexc_c11m12:
        print("[c11m12] call skipped (argument build failed):", repr(_argexc_c11m12), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c11_popen, '_send_signal')
    except Exception as e_get_target_func:
        print(f"[c11m12] Failed to get attribute _send_signal from instance_c11_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=('/tmp/fusil-fixtures/fusil_fixture.bin',), name='c11m12__send_signal')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c11m12] Failed to create thread for _send_signal: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c11m12__send_signal(target_func=target_func):
            print("Starting async task: async_call_c11m12__send_signal", file=stderr)
            time.sleep(0.000758) # Small delay
            try:
                target_func(None)
            except Exception as e_async_call:
                print(f"[c11m12] Exception in async task async_call_c11m12__send_signal: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c11m12__send_signal", file=stderr)
        fuzzer_async_tasks.append(async_call_c11m12__send_signal)

    try:
        res_c11m13 = callMethod("c11m13", instance_c11_popen, "__getstate__",
        verbose=True)
    except Exception as _argexc_c11m13:
        print("[c11m13] call skipped (argument build failed):", repr(_argexc_c11m13), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c11_popen, '__getstate__')
    except Exception as e_get_target_func:
        print(f"[c11m13] Failed to get attribute __getstate__ from instance_c11_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c11m13___getstate__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c11m13] Failed to create thread for __getstate__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c11m13___getstate__(target_func=target_func):
            print("Starting async task: async_call_c11m13___getstate__", file=stderr)
            time.sleep(0.000079) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c11m13] Exception in async task async_call_c11m13___getstate__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c11m13___getstate__", file=stderr)
        fuzzer_async_tasks.append(async_call_c11m13___getstate__)

    try:
        res_c11m14 = callMethod("c11m14", instance_c11_popen, "_send_signal",
            tricky_genericalias,
            8,
        verbose=True)
    except Exception as _argexc_c11m14:
        print("[c11m14] call skipped (argument build failed):", repr(_argexc_c11m14), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c11_popen, '_send_signal')
    except Exception as e_get_target_func:
        print(f"[c11m14] Failed to get attribute _send_signal from instance_c11_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(Exception('fuzzer_generated_exception'), MutatingIterable()), name='c11m14__send_signal')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c11m14] Failed to create thread for _send_signal: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c11m14__send_signal(target_func=target_func):
            print("Starting async task: async_call_c11m14__send_signal", file=stderr)
            time.sleep(0.000792) # Small delay
            try:
                target_func(tuple[weird_classes['weird_set']] | weird_classes['weird_object'] | big_union, "\x99\x19\x11\xC0\x86")
            except Exception as e_async_call:
                print(f"[c11m14] Exception in async task async_call_c11m14__send_signal: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c11m14__send_signal", file=stderr)
        fuzzer_async_tasks.append(async_call_c11m14__send_signal)

    try:
        res_c11m15 = callMethod("c11m15", instance_c11_popen, "duplicate_for_child",
            FailingIterator(),
        verbose=True)
    except Exception as _argexc_c11m15:
        print("[c11m15] call skipped (argument build failed):", repr(_argexc_c11m15), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c11_popen, 'duplicate_for_child')
    except Exception as e_get_target_func:
        print(f"[c11m15] Failed to get attribute duplicate_for_child from instance_c11_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(weird_classes['weird_int'],), name='c11m15_duplicate_for_child')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c11m15] Failed to create thread for duplicate_for_child: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c11m15_duplicate_for_child(target_func=target_func):
            print("Starting async task: async_call_c11m15_duplicate_for_child", file=stderr)
            time.sleep(0.000551) # Small delay
            try:
                target_func(FailingIterator())
            except Exception as e_async_call:
                print(f"[c11m15] Exception in async task async_call_c11m15_duplicate_for_child: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c11m15_duplicate_for_child", file=stderr)
        fuzzer_async_tasks.append(async_call_c11m15_duplicate_for_child)

    print(f"--- Finished fuzzing instance: instance_c11_popen ---", file=stderr)

    del instance_c11_popen # Cleanup instance
    print("[c11] -explicit garbage collection for class instance-", file=stderr)
    collect()

print("[c12] Attempting to instantiate class: Popen", file=stderr)
instance_c12_popen = None # Initialize instance variable
try:
    instance_c12_popen = callFunc('c12_init', 'Popen',
        RaisingInstanceCheckType,
      )
except Exception as e_instantiate:
    instance_c12_popen = None
    print("[c12] Failed to instantiate Popen: {e_instantiate.__class__.__name__} {e_instantiate}", file=stderr)
    instance_c12_popen = None

try:
    print(f"--- (Depth 0) Dispatching Fuzz for: {instance_c12_popen!r} (hint: Popen, prefix: c12_popen_ops) ---", file=stderr)
except Exception as e:
    print(f"--- (Depth 0) Error calling repr() prefix: c12_popen_ops) ---", file=stderr)
if instance_c12_popen is not None:
    if skip_trivial_type(instance_c12_popen):
        print(f'Skipping deep diving on instance_c12_popen {type(instance_c12_popen)}', file=stderr)
    try:
        print(f'Instance {instance_c12_popen!r} (actual type {type(instance_c12_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    except Exception as e:
        print(f'Error printing instance repr() { e } (actual type {type(instance_c12_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    if skip_trivial_type(instance_c12_popen):
        print(f'Skipping deep diving on instance_c12_popen {type(instance_c12_popen)}', file=stderr)
    else:
        print(f'Instance instance_c12_popen (type {type(instance_c12_popen).__name__}) has no specific fuzzer, doing generic calls.', file=stderr)
        c12_popen_ops_generic_methods = []
        try:
            for c12_popen_ops_generic_attr_name in dir(instance_c12_popen):
                if c12_popen_ops_generic_attr_name.startswith('_'): continue
                try:
                    c12_popen_ops_generic_attr_val = getattr(instance_c12_popen, c12_popen_ops_generic_attr_name)
                    if callable(c12_popen_ops_generic_attr_val) and c12_popen_ops_generic_attr_name not in _FUSIL_METHOD_BLACKLIST: c12_popen_ops_generic_methods.append((c12_popen_ops_generic_attr_name, c12_popen_ops_generic_attr_val))
                except Exception: pass
        except Exception: c12_popen_ops_generic_methods = [] # Failed to get methods
        if c12_popen_ops_generic_methods:
            print(f'Found {len(c12_popen_ops_generic_methods)} callable methods for generic fuzzing of instance_c12_popen', file=stderr)
            for _i_c12_popen_ops_generic in range(min(len(c12_popen_ops_generic_methods), 15)):
                c12_popen_ops_generic_method_name_to_call, c12_popen_ops_generic_method_obj_to_call = choice(c12_popen_ops_generic_methods)
                # Conceptual call to generic method fuzzer
                if c12_popen_ops_generic_method_name_to_call not in _FUSIL_METHOD_BLACKLIST: callMethod(f'c12_popen_ops_generic_gen{_i_c12_popen_ops_generic}', instance_c12_popen, c12_popen_ops_generic_method_name_to_call)

if instance_c12_popen is not None and instance_c12_popen is not SENTINEL_VALUE:
    print(f"--- Fuzzing instance: instance_c12_popen (type hint: Popen, prefix: c12m) ---", file=stderr)
    if skip_trivial_type(instance_c12_popen):
        print(f'Skipping deep diving on instance_c12_popen {type(instance_c12_popen)}', file=stderr)
    # General method fuzzing for instance_c12_popen
    try:
        res_c12m1 = callMethod("c12m1", instance_c12_popen, "__new__",
            True,
            17,
            sys.float_info.min / 2,
        verbose=True)
    except Exception as _argexc_c12m1:
        print("[c12m1] call skipped (argument build failed):", repr(_argexc_c12m1), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c12_popen, '__new__')
    except Exception as e_get_target_func:
        print(f"[c12m1] Failed to get attribute __new__ from instance_c12_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(LyingEq(), "\udbff\udfff", dict[weird_classes['weird_complex']]), name='c12m1___new__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c12m1] Failed to create thread for __new__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c12m1___new__(target_func=target_func):
            print("Starting async task: async_call_c12m1___new__", file=stderr)
            time.sleep(0.000507) # Small delay
            try:
                target_func(r"Q\BYFwDNgWhM\w\Ag.dwXP\ZAdCnfck", errback, -150.252)
            except Exception as e_async_call:
                print(f"[c12m1] Exception in async task async_call_c12m1___new__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c12m1___new__", file=stderr)
        fuzzer_async_tasks.append(async_call_c12m1___new__)

    try:
        res_c12m2 = callMethod("c12m2", instance_c12_popen, "__new__",
        verbose=True)
    except Exception as _argexc_c12m2:
        print("[c12m2] call skipped (argument build failed):", repr(_argexc_c12m2), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c12_popen, '__new__')
    except Exception as e_get_target_func:
        print(f"[c12m2] Failed to get attribute __new__ from instance_c12_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c12m2___new__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c12m2] Failed to create thread for __new__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c12m2___new__(target_func=target_func):
            print("Starting async task: async_call_c12m2___new__", file=stderr)
            time.sleep(0.000680) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c12m2] Exception in async task async_call_c12m2___new__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c12m2___new__", file=stderr)
        fuzzer_async_tasks.append(async_call_c12m2___new__)

    try:
        res_c12m3 = callMethod("c12m3", instance_c12_popen, "__ne__",
            TypeFlipIterator(),
        verbose=True)
    except Exception as _argexc_c12m3:
        print("[c12m3] call skipped (argument build failed):", repr(_argexc_c12m3), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c12_popen, '__ne__')
    except Exception as e_get_target_func:
        print(f"[c12m3] Failed to get attribute __ne__ from instance_c12_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(True,), name='c12m3___ne__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c12m3] Failed to create thread for __ne__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c12m3___ne__(target_func=target_func):
            print("Starting async task: async_call_c12m3___ne__", file=stderr)
            time.sleep(0.000829) # Small delay
            try:
                target_func(-68.980)
            except Exception as e_async_call:
                print(f"[c12m3] Exception in async task async_call_c12m3___ne__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c12m3___ne__", file=stderr)
        fuzzer_async_tasks.append(async_call_c12m3___ne__)

    try:
        res_c12m4 = callMethod("c12m4", instance_c12_popen, "__delattr__",
            "\xBBU\x16\xE8\xE2\x88<\xF4V\x8D\xA5\xD815\xA2\xABC",
        verbose=True)
    except Exception as _argexc_c12m4:
        print("[c12m4] call skipped (argument build failed):", repr(_argexc_c12m4), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c12_popen, '__delattr__')
    except Exception as e_get_target_func:
        print(f"[c12m4] Failed to get attribute __delattr__ from instance_c12_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("\x00",), name='c12m4___delattr__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c12m4] Failed to create thread for __delattr__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c12m4___delattr__(target_func=target_func):
            print("Starting async task: async_call_c12m4___delattr__", file=stderr)
            time.sleep(0.000929) # Small delay
            try:
                target_func("/ntb5aUuRON7J0-/c82PLASQWCDaLeKM5swT_6e-Zv8HUoD7EWFr3RUk7caFYB65SZjZeqIDDD0eZRvtN6Fg/NkJ//M/")
            except Exception as e_async_call:
                print(f"[c12m4] Exception in async task async_call_c12m4___delattr__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c12m4___delattr__", file=stderr)
        fuzzer_async_tasks.append(async_call_c12m4___delattr__)

    try:
        res_c12m5 = callMethod("c12m5", instance_c12_popen, "__lt__",
        verbose=True)
    except Exception as _argexc_c12m5:
        print("[c12m5] call skipped (argument build failed):", repr(_argexc_c12m5), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c12_popen, '__lt__')
    except Exception as e_get_target_func:
        print(f"[c12m5] Failed to get attribute __lt__ from instance_c12_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c12m5___lt__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c12m5] Failed to create thread for __lt__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c12m5___lt__(target_func=target_func):
            print("Starting async task: async_call_c12m5___lt__", file=stderr)
            time.sleep(0.000524) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c12m5] Exception in async task async_call_c12m5___lt__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c12m5___lt__", file=stderr)
        fuzzer_async_tasks.append(async_call_c12m5___lt__)

    try:
        res_c12m6 = callMethod("c12m6", instance_c12_popen, "__hash__",
        verbose=True)
    except Exception as _argexc_c12m6:
        print("[c12m6] call skipped (argument build failed):", repr(_argexc_c12m6), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c12_popen, '__hash__')
    except Exception as e_get_target_func:
        print(f"[c12m6] Failed to get attribute __hash__ from instance_c12_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c12m6___hash__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c12m6] Failed to create thread for __hash__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c12m6___hash__(target_func=target_func):
            print("Starting async task: async_call_c12m6___hash__", file=stderr)
            time.sleep(0.000801) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c12m6] Exception in async task async_call_c12m6___hash__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c12m6___hash__", file=stderr)
        fuzzer_async_tasks.append(async_call_c12m6___hash__)

    try:
        res_c12m7 = callMethod("c12m7", instance_c12_popen, "poll",
            "Ce\x96\xCBX\'\xCD\xEB\x88q",
        verbose=True)
    except Exception as _argexc_c12m7:
        print("[c12m7] call skipped (argument build failed):", repr(_argexc_c12m7), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c12_popen, 'poll')
    except Exception as e_get_target_func:
        print(f"[c12m7] Failed to get attribute poll from instance_c12_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("\xD0\xD1\xBA",), name='c12m7_poll')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c12m7] Failed to create thread for poll: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c12m7_poll(target_func=target_func):
            print("Starting async task: async_call_c12m7_poll", file=stderr)
            time.sleep(0.000699) # Small delay
            try:
                target_func(LyingEq())
            except Exception as e_async_call:
                print(f"[c12m7] Exception in async task async_call_c12m7_poll: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c12m7_poll", file=stderr)
        fuzzer_async_tasks.append(async_call_c12m7_poll)

    try:
        res_c12m8 = callMethod("c12m8", instance_c12_popen, "__ge__",
            tricky_recur_a,
        verbose=True)
    except Exception as _argexc_c12m8:
        print("[c12m8] call skipped (argument build failed):", repr(_argexc_c12m8), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c12_popen, '__ge__')
    except Exception as e_get_target_func:
        print(f"[c12m8] Failed to get attribute __ge__ from instance_c12_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(ReentrantClearList(),), name='c12m8___ge__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c12m8] Failed to create thread for __ge__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c12m8___ge__(target_func=target_func):
            print("Starting async task: async_call_c12m8___ge__", file=stderr)
            time.sleep(0.000495) # Small delay
            try:
                target_func(memoryview(b"abc\xe9\xff"))
            except Exception as e_async_call:
                print(f"[c12m8] Exception in async task async_call_c12m8___ge__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c12m8___ge__", file=stderr)
        fuzzer_async_tasks.append(async_call_c12m8___ge__)

    try:
        res_c12m9 = callMethod("c12m9", instance_c12_popen, "__lt__",
            ReentrantClearDict(),
        verbose=True)
    except Exception as _argexc_c12m9:
        print("[c12m9] call skipped (argument build failed):", repr(_argexc_c12m9), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c12_popen, '__lt__')
    except Exception as e_get_target_func:
        print(f"[c12m9] Failed to get attribute __lt__ from instance_c12_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=('/tmp/fusil-fixtures/fusil_fixture.bin',), name='c12m9___lt__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c12m9] Failed to create thread for __lt__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c12m9___lt__(target_func=target_func):
            print("Starting async task: async_call_c12m9___lt__", file=stderr)
            time.sleep(0.000744) # Small delay
            try:
                target_func(weird_classes['weird_int'])
            except Exception as e_async_call:
                print(f"[c12m9] Exception in async task async_call_c12m9___lt__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c12m9___lt__", file=stderr)
        fuzzer_async_tasks.append(async_call_c12m9___lt__)

    try:
        res_c12m10 = callMethod("c12m10", instance_c12_popen, "__reduce_ex__",
            HiddenNameType,
        verbose=True)
    except Exception as _argexc_c12m10:
        print("[c12m10] call skipped (argument build failed):", repr(_argexc_c12m10), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c12_popen, '__reduce_ex__')
    except Exception as e_get_target_func:
        print(f"[c12m10] Failed to get attribute __reduce_ex__ from instance_c12_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(HashBomb(),), name='c12m10___reduce_ex__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c12m10] Failed to create thread for __reduce_ex__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c12m10___reduce_ex__(target_func=target_func):
            print("Starting async task: async_call_c12m10___reduce_ex__", file=stderr)
            time.sleep(0.000452) # Small delay
            try:
                target_func("\x01?L")
            except Exception as e_async_call:
                print(f"[c12m10] Exception in async task async_call_c12m10___reduce_ex__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c12m10___reduce_ex__", file=stderr)
        fuzzer_async_tasks.append(async_call_c12m10___reduce_ex__)

    try:
        res_c12m11 = callMethod("c12m11", instance_c12_popen, "__getattribute__",
            LyingLen(),
        verbose=True)
    except Exception as _argexc_c12m11:
        print("[c12m11] call skipped (argument build failed):", repr(_argexc_c12m11), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c12_popen, '__getattribute__')
    except Exception as e_get_target_func:
        print(f"[c12m11] Failed to get attribute __getattribute__ from instance_c12_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(-43.6,), name='c12m11___getattribute__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c12m11] Failed to create thread for __getattribute__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c12m11___getattribute__(target_func=target_func):
            print("Starting async task: async_call_c12m11___getattribute__", file=stderr)
            time.sleep(0.000288) # Small delay
            try:
                target_func(TypeFlipIterator())
            except Exception as e_async_call:
                print(f"[c12m11] Exception in async task async_call_c12m11___getattribute__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c12m11___getattribute__", file=stderr)
        fuzzer_async_tasks.append(async_call_c12m11___getattribute__)

    try:
        res_c12m12 = callMethod("c12m12", instance_c12_popen, "__getstate__",
        verbose=True)
    except Exception as _argexc_c12m12:
        print("[c12m12] call skipped (argument build failed):", repr(_argexc_c12m12), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c12_popen, '__getstate__')
    except Exception as e_get_target_func:
        print(f"[c12m12] Failed to get attribute __getstate__ from instance_c12_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c12m12___getstate__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c12m12] Failed to create thread for __getstate__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c12m12___getstate__(target_func=target_func):
            print("Starting async task: async_call_c12m12___getstate__", file=stderr)
            time.sleep(0.000647) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c12m12] Exception in async task async_call_c12m12___getstate__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c12m12___getstate__", file=stderr)
        fuzzer_async_tasks.append(async_call_c12m12___getstate__)

    try:
        res_c12m13 = callMethod("c12m13", instance_c12_popen, "__ge__",
            LenBomb(),
        verbose=True)
    except Exception as _argexc_c12m13:
        print("[c12m13] call skipped (argument build failed):", repr(_argexc_c12m13), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c12_popen, '__ge__')
    except Exception as e_get_target_func:
        print(f"[c12m13] Failed to get attribute __ge__ from instance_c12_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("B\x82\xC9\xEA",), name='c12m13___ge__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c12m13] Failed to create thread for __ge__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c12m13___ge__(target_func=target_func):
            print("Starting async task: async_call_c12m13___ge__", file=stderr)
            time.sleep(0.000418) # Small delay
            try:
                target_func(tricky_module2)
            except Exception as e_async_call:
                print(f"[c12m13] Exception in async task async_call_c12m13___ge__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c12m13___ge__", file=stderr)
        fuzzer_async_tasks.append(async_call_c12m13___ge__)

    try:
        res_c12m14 = callMethod("c12m14", instance_c12_popen, "__new__",
            ReentrantClearList(),
            LyingLen(),
            RaisingInstanceCheckType,
        verbose=True)
    except Exception as _argexc_c12m14:
        print("[c12m14] call skipped (argument build failed):", repr(_argexc_c12m14), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c12_popen, '__new__')
    except Exception as e_get_target_func:
        print(f"[c12m14] Failed to get attribute __new__ from instance_c12_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(memoryview(bytearray(b"abc\xe9\xff")), errback, "\xEB\x81\xB0\x7F\xB2\xB1"), name='c12m14___new__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c12m14] Failed to create thread for __new__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c12m14___new__(target_func=target_func):
            print("Starting async task: async_call_c12m14___new__", file=stderr)
            time.sleep(0.000341) # Small delay
            try:
                target_func(weird_classes['weird_bytearray'], dict[weird_classes['weird_list']] | weird_classes['weird_bytearray'] | big_union, True)
            except Exception as e_async_call:
                print(f"[c12m14] Exception in async task async_call_c12m14___new__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c12m14___new__", file=stderr)
        fuzzer_async_tasks.append(async_call_c12m14___new__)

    try:
        res_c12m15 = callMethod("c12m15", instance_c12_popen, "__lt__",
            -35555418243969802,
        verbose=True)
    except Exception as _argexc_c12m15:
        print("[c12m15] call skipped (argument build failed):", repr(_argexc_c12m15), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c12_popen, '__lt__')
    except Exception as e_get_target_func:
        print(f"[c12m15] Failed to get attribute __lt__ from instance_c12_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(tricky_classmethod_descriptor,), name='c12m15___lt__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c12m15] Failed to create thread for __lt__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c12m15___lt__(target_func=target_func):
            print("Starting async task: async_call_c12m15___lt__", file=stderr)
            time.sleep(0.000077) # Small delay
            try:
                target_func("A" * (2**10))
            except Exception as e_async_call:
                print(f"[c12m15] Exception in async task async_call_c12m15___lt__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c12m15___lt__", file=stderr)
        fuzzer_async_tasks.append(async_call_c12m15___lt__)

    print(f"--- Finished fuzzing instance: instance_c12_popen ---", file=stderr)

    del instance_c12_popen # Cleanup instance
    print("[c12] -explicit garbage collection for class instance-", file=stderr)
    collect()

print("[c13] Attempting to instantiate class: Popen", file=stderr)
instance_c13_popen = None # Initialize instance variable
try:
    instance_c13_popen = callFunc('c13_init', 'Popen',
        "BQ\x12\xBD\xE6",
      )
except Exception as e_instantiate:
    instance_c13_popen = None
    print("[c13] Failed to instantiate Popen: {e_instantiate.__class__.__name__} {e_instantiate}", file=stderr)
    instance_c13_popen = None

try:
    print(f"--- (Depth 0) Dispatching Fuzz for: {instance_c13_popen!r} (hint: Popen, prefix: c13_popen_ops) ---", file=stderr)
except Exception as e:
    print(f"--- (Depth 0) Error calling repr() prefix: c13_popen_ops) ---", file=stderr)
if instance_c13_popen is not None:
    if skip_trivial_type(instance_c13_popen):
        print(f'Skipping deep diving on instance_c13_popen {type(instance_c13_popen)}', file=stderr)
    try:
        print(f'Instance {instance_c13_popen!r} (actual type {type(instance_c13_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    except Exception as e:
        print(f'Error printing instance repr() { e } (actual type {type(instance_c13_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    if skip_trivial_type(instance_c13_popen):
        print(f'Skipping deep diving on instance_c13_popen {type(instance_c13_popen)}', file=stderr)
    else:
        print(f'Instance instance_c13_popen (type {type(instance_c13_popen).__name__}) has no specific fuzzer, doing generic calls.', file=stderr)
        c13_popen_ops_generic_methods = []
        try:
            for c13_popen_ops_generic_attr_name in dir(instance_c13_popen):
                if c13_popen_ops_generic_attr_name.startswith('_'): continue
                try:
                    c13_popen_ops_generic_attr_val = getattr(instance_c13_popen, c13_popen_ops_generic_attr_name)
                    if callable(c13_popen_ops_generic_attr_val) and c13_popen_ops_generic_attr_name not in _FUSIL_METHOD_BLACKLIST: c13_popen_ops_generic_methods.append((c13_popen_ops_generic_attr_name, c13_popen_ops_generic_attr_val))
                except Exception: pass
        except Exception: c13_popen_ops_generic_methods = [] # Failed to get methods
        if c13_popen_ops_generic_methods:
            print(f'Found {len(c13_popen_ops_generic_methods)} callable methods for generic fuzzing of instance_c13_popen', file=stderr)
            for _i_c13_popen_ops_generic in range(min(len(c13_popen_ops_generic_methods), 15)):
                c13_popen_ops_generic_method_name_to_call, c13_popen_ops_generic_method_obj_to_call = choice(c13_popen_ops_generic_methods)
                # Conceptual call to generic method fuzzer
                if c13_popen_ops_generic_method_name_to_call not in _FUSIL_METHOD_BLACKLIST: callMethod(f'c13_popen_ops_generic_gen{_i_c13_popen_ops_generic}', instance_c13_popen, c13_popen_ops_generic_method_name_to_call)

if instance_c13_popen is not None and instance_c13_popen is not SENTINEL_VALUE:
    print(f"--- Fuzzing instance: instance_c13_popen (type hint: Popen, prefix: c13m) ---", file=stderr)
    if skip_trivial_type(instance_c13_popen):
        print(f'Skipping deep diving on instance_c13_popen {type(instance_c13_popen)}', file=stderr)
    # General method fuzzing for instance_c13_popen
    try:
        res_c13m1 = callMethod("c13m1", instance_c13_popen, "__getattribute__",
            -5,
        verbose=True)
    except Exception as _argexc_c13m1:
        print("[c13m1] call skipped (argument build failed):", repr(_argexc_c13m1), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c13_popen, '__getattribute__')
    except Exception as e_get_target_func:
        print(f"[c13m1] Failed to get attribute __getattribute__ from instance_c13_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=('/tmp/fusil-fixtures/fusil_fixture.bin',), name='c13m1___getattribute__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c13m1] Failed to create thread for __getattribute__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c13m1___getattribute__(target_func=target_func):
            print("Starting async task: async_call_c13m1___getattribute__", file=stderr)
            time.sleep(0.000591) # Small delay
            try:
                target_func(ReadBomb())
            except Exception as e_async_call:
                print(f"[c13m1] Exception in async task async_call_c13m1___getattribute__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c13m1___getattribute__", file=stderr)
        fuzzer_async_tasks.append(async_call_c13m1___getattribute__)

    try:
        res_c13m2 = callMethod("c13m2", instance_c13_popen, "__dir__",
        verbose=True)
    except Exception as _argexc_c13m2:
        print("[c13m2] call skipped (argument build failed):", repr(_argexc_c13m2), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c13_popen, '__dir__')
    except Exception as e_get_target_func:
        print(f"[c13m2] Failed to get attribute __dir__ from instance_c13_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c13m2___dir__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c13m2] Failed to create thread for __dir__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c13m2___dir__(target_func=target_func):
            print("Starting async task: async_call_c13m2___dir__", file=stderr)
            time.sleep(0.000004) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c13m2] Exception in async task async_call_c13m2___dir__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c13m2___dir__", file=stderr)
        fuzzer_async_tasks.append(async_call_c13m2___dir__)

    try:
        res_c13m3 = callMethod("c13m3", instance_c13_popen, "__repr__",
        verbose=True)
    except Exception as _argexc_c13m3:
        print("[c13m3] call skipped (argument build failed):", repr(_argexc_c13m3), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c13_popen, '__repr__')
    except Exception as e_get_target_func:
        print(f"[c13m3] Failed to get attribute __repr__ from instance_c13_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c13m3___repr__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c13m3] Failed to create thread for __repr__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c13m3___repr__(target_func=target_func):
            print("Starting async task: async_call_c13m3___repr__", file=stderr)
            time.sleep(0.000013) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c13m3] Exception in async task async_call_c13m3___repr__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c13m3___repr__", file=stderr)
        fuzzer_async_tasks.append(async_call_c13m3___repr__)

    try:
        res_c13m4 = callMethod("c13m4", instance_c13_popen, "__ge__",
            ReadBomb(),
        verbose=True)
    except Exception as _argexc_c13m4:
        print("[c13m4] call skipped (argument build failed):", repr(_argexc_c13m4), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c13_popen, '__ge__')
    except Exception as e_get_target_func:
        print(f"[c13m4] Failed to get attribute __ge__ from instance_c13_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("\udbff\udfff",), name='c13m4___ge__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c13m4] Failed to create thread for __ge__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c13m4___ge__(target_func=target_func):
            print("Starting async task: async_call_c13m4___ge__", file=stderr)
            time.sleep(0.000879) # Small delay
            try:
                target_func(-13)
            except Exception as e_async_call:
                print(f"[c13m4] Exception in async task async_call_c13m4___ge__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c13m4___ge__", file=stderr)
        fuzzer_async_tasks.append(async_call_c13m4___ge__)

    try:
        res_c13m5 = callMethod("c13m5", instance_c13_popen, "__setattr__",
            [[[[[[[[[[[[[[]]]]]]]]]]]]]],
            Template("\x00", Interpolation(weird_instances['weird_complex_-2**31-1'], "name")),
        verbose=True)
    except Exception as _argexc_c13m5:
        print("[c13m5] call skipped (argument build failed):", repr(_argexc_c13m5), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c13_popen, '__setattr__')
    except Exception as e_get_target_func:
        print(f"[c13m5] Failed to get attribute __setattr__ from instance_c13_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(DescriptorBomb(), list[weird_classes['weird_object']] | weird_classes['weird_str'] | big_union), name='c13m5___setattr__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c13m5] Failed to create thread for __setattr__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c13m5___setattr__(target_func=target_func):
            print("Starting async task: async_call_c13m5___setattr__", file=stderr)
            time.sleep(0.000041) # Small delay
            try:
                target_func(FilenoBomb(), LyingInplace())
            except Exception as e_async_call:
                print(f"[c13m5] Exception in async task async_call_c13m5___setattr__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c13m5___setattr__", file=stderr)
        fuzzer_async_tasks.append(async_call_c13m5___setattr__)

    try:
        res_c13m6 = callMethod("c13m6", instance_c13_popen, "__eq__",
            "\xEC\'B\xA6\xA4\xEF\x90+\x15s\xB9{\x1D\x8B\xAE\xBEr\xDE]P",
        verbose=True)
    except Exception as _argexc_c13m6:
        print("[c13m6] call skipped (argument build failed):", repr(_argexc_c13m6), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c13_popen, '__eq__')
    except Exception as e_get_target_func:
        print(f"[c13m6] Failed to get attribute __eq__ from instance_c13_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(Evil(),), name='c13m6___eq__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c13m6] Failed to create thread for __eq__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c13m6___eq__(target_func=target_func):
            print("Starting async task: async_call_c13m6___eq__", file=stderr)
            time.sleep(0.000269) # Small delay
            try:
                target_func(True)
            except Exception as e_async_call:
                print(f"[c13m6] Exception in async task async_call_c13m6___eq__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c13m6___eq__", file=stderr)
        fuzzer_async_tasks.append(async_call_c13m6___eq__)

    try:
        res_c13m7 = callMethod("c13m7", instance_c13_popen, "__reduce_ex__",
            int,
        verbose=True)
    except Exception as _argexc_c13m7:
        print("[c13m7] call skipped (argument build failed):", repr(_argexc_c13m7), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c13_popen, '__reduce_ex__')
    except Exception as e_get_target_func:
        print(f"[c13m7] Failed to get attribute __reduce_ex__ from instance_c13_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(MagicMock,), name='c13m7___reduce_ex__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c13m7] Failed to create thread for __reduce_ex__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c13m7___reduce_ex__(target_func=target_func):
            print("Starting async task: async_call_c13m7___reduce_ex__", file=stderr)
            time.sleep(0.000596) # Small delay
            try:
                target_func(None)
            except Exception as e_async_call:
                print(f"[c13m7] Exception in async task async_call_c13m7___reduce_ex__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c13m7___reduce_ex__", file=stderr)
        fuzzer_async_tasks.append(async_call_c13m7___reduce_ex__)

    try:
        res_c13m8 = callMethod("c13m8", instance_c13_popen, "__le__",
            None,
        verbose=True)
    except Exception as _argexc_c13m8:
        print("[c13m8] call skipped (argument build failed):", repr(_argexc_c13m8), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c13_popen, '__le__')
    except Exception as e_get_target_func:
        print(f"[c13m8] Failed to get attribute __le__ from instance_c13_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(tricky_instance,), name='c13m8___le__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c13m8] Failed to create thread for __le__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c13m8___le__(target_func=target_func):
            print("Starting async task: async_call_c13m8___le__", file=stderr)
            time.sleep(0.000577) # Small delay
            try:
                target_func(LyingLen())
            except Exception as e_async_call:
                print(f"[c13m8] Exception in async task async_call_c13m8___le__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c13m8___le__", file=stderr)
        fuzzer_async_tasks.append(async_call_c13m8___le__)

    try:
        res_c13m9 = callMethod("c13m9", instance_c13_popen, "__le__",
        verbose=True)
    except Exception as _argexc_c13m9:
        print("[c13m9] call skipped (argument build failed):", repr(_argexc_c13m9), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c13_popen, '__le__')
    except Exception as e_get_target_func:
        print(f"[c13m9] Failed to get attribute __le__ from instance_c13_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c13m9___le__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c13m9] Failed to create thread for __le__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c13m9___le__(target_func=target_func):
            print("Starting async task: async_call_c13m9___le__", file=stderr)
            time.sleep(0.000100) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c13m9] Exception in async task async_call_c13m9___le__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c13m9___le__", file=stderr)
        fuzzer_async_tasks.append(async_call_c13m9___le__)

    try:
        res_c13m10 = callMethod("c13m10", instance_c13_popen, "__getstate__",
        verbose=True)
    except Exception as _argexc_c13m10:
        print("[c13m10] call skipped (argument build failed):", repr(_argexc_c13m10), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c13_popen, '__getstate__')
    except Exception as e_get_target_func:
        print(f"[c13m10] Failed to get attribute __getstate__ from instance_c13_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c13m10___getstate__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c13m10] Failed to create thread for __getstate__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c13m10___getstate__(target_func=target_func):
            print("Starting async task: async_call_c13m10___getstate__", file=stderr)
            time.sleep(0.000694) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c13m10] Exception in async task async_call_c13m10___getstate__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c13m10___getstate__", file=stderr)
        fuzzer_async_tasks.append(async_call_c13m10___getstate__)

    try:
        res_c13m11 = callMethod("c13m11", instance_c13_popen, "__eq__",
        verbose=True)
    except Exception as _argexc_c13m11:
        print("[c13m11] call skipped (argument build failed):", repr(_argexc_c13m11), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c13_popen, '__eq__')
    except Exception as e_get_target_func:
        print(f"[c13m11] Failed to get attribute __eq__ from instance_c13_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c13m11___eq__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c13m11] Failed to create thread for __eq__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c13m11___eq__(target_func=target_func):
            print("Starting async task: async_call_c13m11___eq__", file=stderr)
            time.sleep(0.000328) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c13m11] Exception in async task async_call_c13m11___eq__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c13m11___eq__", file=stderr)
        fuzzer_async_tasks.append(async_call_c13m11___eq__)

    try:
        res_c13m12 = callMethod("c13m12", instance_c13_popen, "__eq__",
            tricky_function,
        verbose=True)
    except Exception as _argexc_c13m12:
        print("[c13m12] call skipped (argument build failed):", repr(_argexc_c13m12), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c13_popen, '__eq__')
    except Exception as e_get_target_func:
        print(f"[c13m12] Failed to get attribute __eq__ from instance_c13_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(GrowingLen(),), name='c13m12___eq__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c13m12] Failed to create thread for __eq__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c13m12___eq__(target_func=target_func):
            print("Starting async task: async_call_c13m12___eq__", file=stderr)
            time.sleep(0.000887) # Small delay
            try:
                target_func(MutatingIterable())
            except Exception as e_async_call:
                print(f"[c13m12] Exception in async task async_call_c13m12___eq__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c13m12___eq__", file=stderr)
        fuzzer_async_tasks.append(async_call_c13m12___eq__)

    try:
        res_c13m13 = callMethod("c13m13", instance_c13_popen, "kill",
        verbose=True)
    except Exception as _argexc_c13m13:
        print("[c13m13] call skipped (argument build failed):", repr(_argexc_c13m13), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c13_popen, 'kill')
    except Exception as e_get_target_func:
        print(f"[c13m13] Failed to get attribute kill from instance_c13_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c13m13_kill')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c13m13] Failed to create thread for kill: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c13m13_kill(target_func=target_func):
            print("Starting async task: async_call_c13m13_kill", file=stderr)
            time.sleep(0.000988) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c13m13] Exception in async task async_call_c13m13_kill: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c13m13_kill", file=stderr)
        fuzzer_async_tasks.append(async_call_c13m13_kill)

    try:
        res_c13m14 = callMethod("c13m14", instance_c13_popen, "__new__",
            '/tmp/fusil-fixtures/fusil_fixture.txt',
            errback,
            "J/7/",
        verbose=True)
    except Exception as _argexc_c13m14:
        print("[c13m14] call skipped (argument build failed):", repr(_argexc_c13m14), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c13_popen, '__new__')
    except Exception as e_get_target_func:
        print(f"[c13m14] Failed to get attribute __new__ from instance_c13_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(b"\xDA\x01\xEF\x6C\xB6\x27\x97\x5B\x90\x98\x8D\x7A\xDC\x48\x48\xA1\x9C\xF7\x68", EqBomb(), bytearray(b"test")), name='c13m14___new__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c13m14] Failed to create thread for __new__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c13m14___new__(target_func=target_func):
            print("Starting async task: async_call_c13m14___new__", file=stderr)
            time.sleep(0.000107) # Small delay
            try:
                target_func('/tmp/fusil-fixtures/fusil_fixture.txt', errback, "\u4F58\u9B37\uBB8F\uE17C\uAE17\u4CE8\uD00D\uB91C\uC0EF\uE7C0\u9C6D\u46B1\u697A\uBDF4\u1885\uFC12\u8190")
            except Exception as e_async_call:
                print(f"[c13m14] Exception in async task async_call_c13m14___new__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c13m14___new__", file=stderr)
        fuzzer_async_tasks.append(async_call_c13m14___new__)

    try:
        res_c13m15 = callMethod("c13m15", instance_c13_popen, "__init_subclass__",
        verbose=True)
    except Exception as _argexc_c13m15:
        print("[c13m15] call skipped (argument build failed):", repr(_argexc_c13m15), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c13_popen, '__init_subclass__')
    except Exception as e_get_target_func:
        print(f"[c13m15] Failed to get attribute __init_subclass__ from instance_c13_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c13m15___init_subclass__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c13m15] Failed to create thread for __init_subclass__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c13m15___init_subclass__(target_func=target_func):
            print("Starting async task: async_call_c13m15___init_subclass__", file=stderr)
            time.sleep(0.000957) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c13m15] Exception in async task async_call_c13m15___init_subclass__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c13m15___init_subclass__", file=stderr)
        fuzzer_async_tasks.append(async_call_c13m15___init_subclass__)

    print(f"--- Finished fuzzing instance: instance_c13_popen ---", file=stderr)

    del instance_c13_popen # Cleanup instance
    print("[c13] -explicit garbage collection for class instance-", file=stderr)
    collect()

print("[c14] Attempting to instantiate class: Popen", file=stderr)
instance_c14_popen = None # Initialize instance variable
try:
    instance_c14_popen = callFunc('c14_init', 'Popen',
        863.806,
      )
except Exception as e_instantiate:
    instance_c14_popen = None
    print("[c14] Failed to instantiate Popen: {e_instantiate.__class__.__name__} {e_instantiate}", file=stderr)
    instance_c14_popen = None

try:
    print(f"--- (Depth 0) Dispatching Fuzz for: {instance_c14_popen!r} (hint: Popen, prefix: c14_popen_ops) ---", file=stderr)
except Exception as e:
    print(f"--- (Depth 0) Error calling repr() prefix: c14_popen_ops) ---", file=stderr)
if instance_c14_popen is not None:
    if skip_trivial_type(instance_c14_popen):
        print(f'Skipping deep diving on instance_c14_popen {type(instance_c14_popen)}', file=stderr)
    try:
        print(f'Instance {instance_c14_popen!r} (actual type {type(instance_c14_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    except Exception as e:
        print(f'Error printing instance repr() { e } (actual type {type(instance_c14_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    if skip_trivial_type(instance_c14_popen):
        print(f'Skipping deep diving on instance_c14_popen {type(instance_c14_popen)}', file=stderr)
    else:
        print(f'Instance instance_c14_popen (type {type(instance_c14_popen).__name__}) has no specific fuzzer, doing generic calls.', file=stderr)
        c14_popen_ops_generic_methods = []
        try:
            for c14_popen_ops_generic_attr_name in dir(instance_c14_popen):
                if c14_popen_ops_generic_attr_name.startswith('_'): continue
                try:
                    c14_popen_ops_generic_attr_val = getattr(instance_c14_popen, c14_popen_ops_generic_attr_name)
                    if callable(c14_popen_ops_generic_attr_val) and c14_popen_ops_generic_attr_name not in _FUSIL_METHOD_BLACKLIST: c14_popen_ops_generic_methods.append((c14_popen_ops_generic_attr_name, c14_popen_ops_generic_attr_val))
                except Exception: pass
        except Exception: c14_popen_ops_generic_methods = [] # Failed to get methods
        if c14_popen_ops_generic_methods:
            print(f'Found {len(c14_popen_ops_generic_methods)} callable methods for generic fuzzing of instance_c14_popen', file=stderr)
            for _i_c14_popen_ops_generic in range(min(len(c14_popen_ops_generic_methods), 15)):
                c14_popen_ops_generic_method_name_to_call, c14_popen_ops_generic_method_obj_to_call = choice(c14_popen_ops_generic_methods)
                # Conceptual call to generic method fuzzer
                if c14_popen_ops_generic_method_name_to_call not in _FUSIL_METHOD_BLACKLIST: callMethod(f'c14_popen_ops_generic_gen{_i_c14_popen_ops_generic}', instance_c14_popen, c14_popen_ops_generic_method_name_to_call)

if instance_c14_popen is not None and instance_c14_popen is not SENTINEL_VALUE:
    print(f"--- Fuzzing instance: instance_c14_popen (type hint: Popen, prefix: c14m) ---", file=stderr)
    if skip_trivial_type(instance_c14_popen):
        print(f'Skipping deep diving on instance_c14_popen {type(instance_c14_popen)}', file=stderr)
    # General method fuzzing for instance_c14_popen
    try:
        res_c14m1 = callMethod("c14m1", instance_c14_popen, "__init__",
            dict[weird_classes['weird_deque']],
        verbose=True)
    except Exception as _argexc_c14m1:
        print("[c14m1] call skipped (argument build failed):", repr(_argexc_c14m1), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c14_popen, '__init__')
    except Exception as e_get_target_func:
        print(f"[c14m1] Failed to get attribute __init__ from instance_c14_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(tricky_cell,), name='c14m1___init__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c14m1] Failed to create thread for __init__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c14m1___init__(target_func=target_func):
            print("Starting async task: async_call_c14m1___init__", file=stderr)
            time.sleep(0.000310) # Small delay
            try:
                target_func(object())
            except Exception as e_async_call:
                print(f"[c14m1] Exception in async task async_call_c14m1___init__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c14m1___init__", file=stderr)
        fuzzer_async_tasks.append(async_call_c14m1___init__)

    try:
        res_c14m2 = callMethod("c14m2", instance_c14_popen, "__le__",
            weird_classes['weird_float'],
        verbose=True)
    except Exception as _argexc_c14m2:
        print("[c14m2] call skipped (argument build failed):", repr(_argexc_c14m2), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c14_popen, '__le__')
    except Exception as e_get_target_func:
        print(f"[c14m2] Failed to get attribute __le__ from instance_c14_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(r"zW.n.APv\dh..ru\d\WI\D..?EI.\SMx.\ZD.GIlBdq+dhQa*",), name='c14m2___le__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c14m2] Failed to create thread for __le__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c14m2___le__(target_func=target_func):
            print("Starting async task: async_call_c14m2___le__", file=stderr)
            time.sleep(0.000034) # Small delay
            try:
                target_func(tuple[weird_classes['weird_object']] | weird_classes['weird_set'] | big_union)
            except Exception as e_async_call:
                print(f"[c14m2] Exception in async task async_call_c14m2___le__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c14m2___le__", file=stderr)
        fuzzer_async_tasks.append(async_call_c14m2___le__)

    try:
        res_c14m3 = callMethod("c14m3", instance_c14_popen, "__hash__",
        verbose=True)
    except Exception as _argexc_c14m3:
        print("[c14m3] call skipped (argument build failed):", repr(_argexc_c14m3), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c14_popen, '__hash__')
    except Exception as e_get_target_func:
        print(f"[c14m3] Failed to get attribute __hash__ from instance_c14_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c14m3___hash__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c14m3] Failed to create thread for __hash__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c14m3___hash__(target_func=target_func):
            print("Starting async task: async_call_c14m3___hash__", file=stderr)
            time.sleep(0.000948) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c14m3] Exception in async task async_call_c14m3___hash__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c14m3___hash__", file=stderr)
        fuzzer_async_tasks.append(async_call_c14m3___hash__)

    try:
        res_c14m4 = callMethod("c14m4", instance_c14_popen, "__new__",
            tricky_code,
            WrongTypeFile(),
            "/./OQJjCRYUTTof41KBvCPtEsAECYclXw.qzE0q//j-58MivqqWGhHnCE-OGJX.4SBy-X/DwZN64/xqH/LlOQV",
        verbose=True)
    except Exception as _argexc_c14m4:
        print("[c14m4] call skipped (argument build failed):", repr(_argexc_c14m4), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c14_popen, '__new__')
    except Exception as e_get_target_func:
        print(f"[c14m4] Failed to get attribute __new__ from instance_c14_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(FilenoBomb(), b"\x89\x8A\x5A\xD2\x5F\x52\xA4\x12\x32\x9D\x02\xD7\x08\x37\x2E\xB3\xDE\x24", tricky_list_with_cycle), name='c14m4___new__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c14m4] Failed to create thread for __new__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c14m4___new__(target_func=target_func):
            print("Starting async task: async_call_c14m4___new__", file=stderr)
            time.sleep(0.000060) # Small delay
            try:
                target_func(True, TrickyClass, Exception('fuzzer_generated_exception'))
            except Exception as e_async_call:
                print(f"[c14m4] Exception in async task async_call_c14m4___new__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c14m4___new__", file=stderr)
        fuzzer_async_tasks.append(async_call_c14m4___new__)

    try:
        res_c14m5 = callMethod("c14m5", instance_c14_popen, "__init__",
            FailingIterator(),
        verbose=True)
    except Exception as _argexc_c14m5:
        print("[c14m5] call skipped (argument build failed):", repr(_argexc_c14m5), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c14_popen, '__init__')
    except Exception as e_get_target_func:
        print(f"[c14m5] Failed to get attribute __init__ from instance_c14_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(None,), name='c14m5___init__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c14m5] Failed to create thread for __init__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c14m5___init__(target_func=target_func):
            print("Starting async task: async_call_c14m5___init__", file=stderr)
            time.sleep(0.000039) # Small delay
            try:
                target_func(-8)
            except Exception as e_async_call:
                print(f"[c14m5] Exception in async task async_call_c14m5___init__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c14m5___init__", file=stderr)
        fuzzer_async_tasks.append(async_call_c14m5___init__)

    try:
        res_c14m6 = callMethod("c14m6", instance_c14_popen, "_send_signal",
            Exception('fuzzer_generated_exception'),
        verbose=True)
    except Exception as _argexc_c14m6:
        print("[c14m6] call skipped (argument build failed):", repr(_argexc_c14m6), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c14_popen, '_send_signal')
    except Exception as e_get_target_func:
        print(f"[c14m6] Failed to get attribute _send_signal from instance_c14_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(Exception('fuzzer_generated_exception'),), name='c14m6__send_signal')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c14m6] Failed to create thread for _send_signal: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c14m6__send_signal(target_func=target_func):
            print("Starting async task: async_call_c14m6__send_signal", file=stderr)
            time.sleep(0.000226) # Small delay
            try:
                target_func(LenBomb())
            except Exception as e_async_call:
                print(f"[c14m6] Exception in async task async_call_c14m6__send_signal: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c14m6__send_signal", file=stderr)
        fuzzer_async_tasks.append(async_call_c14m6__send_signal)

    try:
        res_c14m7 = callMethod("c14m7", instance_c14_popen, "__getstate__",
        verbose=True)
    except Exception as _argexc_c14m7:
        print("[c14m7] call skipped (argument build failed):", repr(_argexc_c14m7), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c14_popen, '__getstate__')
    except Exception as e_get_target_func:
        print(f"[c14m7] Failed to get attribute __getstate__ from instance_c14_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c14m7___getstate__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c14m7] Failed to create thread for __getstate__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c14m7___getstate__(target_func=target_func):
            print("Starting async task: async_call_c14m7___getstate__", file=stderr)
            time.sleep(0.000307) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c14m7] Exception in async task async_call_c14m7___getstate__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c14m7___getstate__", file=stderr)
        fuzzer_async_tasks.append(async_call_c14m7___getstate__)

    try:
        res_c14m8 = callMethod("c14m8", instance_c14_popen, "__getattribute__",
            WrongTypeFile(),
        verbose=True)
    except Exception as _argexc_c14m8:
        print("[c14m8] call skipped (argument build failed):", repr(_argexc_c14m8), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c14_popen, '__getattribute__')
    except Exception as e_get_target_func:
        print(f"[c14m8] Failed to get attribute __getattribute__ from instance_c14_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("\x00",), name='c14m8___getattribute__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c14m8] Failed to create thread for __getattribute__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c14m8___getattribute__(target_func=target_func):
            print("Starting async task: async_call_c14m8___getattribute__", file=stderr)
            time.sleep(0.000086) # Small delay
            try:
                target_func(711828266886495347)
            except Exception as e_async_call:
                print(f"[c14m8] Exception in async task async_call_c14m8___getattribute__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c14m8___getattribute__", file=stderr)
        fuzzer_async_tasks.append(async_call_c14m8___getattribute__)

    try:
        res_c14m9 = callMethod("c14m9", instance_c14_popen, "__new__",
            sys.maxsize,
            "\x00",
            RaisingInstanceCheckType,
        verbose=True)
    except Exception as _argexc_c14m9:
        print("[c14m9] call skipped (argument build failed):", repr(_argexc_c14m9), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c14_popen, '__new__')
    except Exception as e_get_target_func:
        print(f"[c14m9] Failed to get attribute __new__ from instance_c14_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(None, "\udbff\udfff", ReprBomb()), name='c14m9___new__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c14m9] Failed to create thread for __new__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c14m9___new__(target_func=target_func):
            print("Starting async task: async_call_c14m9___new__", file=stderr)
            time.sleep(0.000066) # Small delay
            try:
                target_func("\u055A\uB0CB\u47B5\u3A3C\u9B11\u3748\u5B1D\u9B82\u9AB0\uBE80\u24A5\uD005\uF805\u5A08\u0AC4\u485E\u8619", -12, True)
            except Exception as e_async_call:
                print(f"[c14m9] Exception in async task async_call_c14m9___new__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c14m9___new__", file=stderr)
        fuzzer_async_tasks.append(async_call_c14m9___new__)

    try:
        res_c14m10 = callMethod("c14m10", instance_c14_popen, "__repr__",
        verbose=True)
    except Exception as _argexc_c14m10:
        print("[c14m10] call skipped (argument build failed):", repr(_argexc_c14m10), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c14_popen, '__repr__')
    except Exception as e_get_target_func:
        print(f"[c14m10] Failed to get attribute __repr__ from instance_c14_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c14m10___repr__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c14m10] Failed to create thread for __repr__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c14m10___repr__(target_func=target_func):
            print("Starting async task: async_call_c14m10___repr__", file=stderr)
            time.sleep(0.000972) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c14m10] Exception in async task async_call_c14m10___repr__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c14m10___repr__", file=stderr)
        fuzzer_async_tasks.append(async_call_c14m10___repr__)

    try:
        res_c14m11 = callMethod("c14m11", instance_c14_popen, "__gt__",
            memoryview(b"abc\xe9\xff"),
        verbose=True)
    except Exception as _argexc_c14m11:
        print("[c14m11] call skipped (argument build failed):", repr(_argexc_c14m11), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c14_popen, '__gt__')
    except Exception as e_get_target_func:
        print(f"[c14m11] Failed to get attribute __gt__ from instance_c14_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(Liar2,), name='c14m11___gt__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c14m11] Failed to create thread for __gt__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c14m11___gt__(target_func=target_func):
            print("Starting async task: async_call_c14m11___gt__", file=stderr)
            time.sleep(0.000580) # Small delay
            try:
                target_func("\u233D\u3DD6\u0BCA\u210B\u5413\u6D92\uA2E4\uDE3A\u8E73")
            except Exception as e_async_call:
                print(f"[c14m11] Exception in async task async_call_c14m11___gt__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c14m11___gt__", file=stderr)
        fuzzer_async_tasks.append(async_call_c14m11___gt__)

    try:
        res_c14m12 = callMethod("c14m12", instance_c14_popen, "terminate",
        verbose=True)
    except Exception as _argexc_c14m12:
        print("[c14m12] call skipped (argument build failed):", repr(_argexc_c14m12), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c14_popen, 'terminate')
    except Exception as e_get_target_func:
        print(f"[c14m12] Failed to get attribute terminate from instance_c14_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c14m12_terminate')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c14m12] Failed to create thread for terminate: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c14m12_terminate(target_func=target_func):
            print("Starting async task: async_call_c14m12_terminate", file=stderr)
            time.sleep(0.000215) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c14m12] Exception in async task async_call_c14m12_terminate: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c14m12_terminate", file=stderr)
        fuzzer_async_tasks.append(async_call_c14m12_terminate)

    try:
        res_c14m13 = callMethod("c14m13", instance_c14_popen, "__getattribute__",
            12,
        verbose=True)
    except Exception as _argexc_c14m13:
        print("[c14m13] call skipped (argument build failed):", repr(_argexc_c14m13), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c14_popen, '__getattribute__')
    except Exception as e_get_target_func:
        print(f"[c14m13] Failed to get attribute __getattribute__ from instance_c14_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(53160933,), name='c14m13___getattribute__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c14m13] Failed to create thread for __getattribute__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c14m13___getattribute__(target_func=target_func):
            print("Starting async task: async_call_c14m13___getattribute__", file=stderr)
            time.sleep(0.000471) # Small delay
            try:
                target_func(None)
            except Exception as e_async_call:
                print(f"[c14m13] Exception in async task async_call_c14m13___getattribute__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c14m13___getattribute__", file=stderr)
        fuzzer_async_tasks.append(async_call_c14m13___getattribute__)

    try:
        res_c14m14 = callMethod("c14m14", instance_c14_popen, "__ne__",
        verbose=True)
    except Exception as _argexc_c14m14:
        print("[c14m14] call skipped (argument build failed):", repr(_argexc_c14m14), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c14_popen, '__ne__')
    except Exception as e_get_target_func:
        print(f"[c14m14] Failed to get attribute __ne__ from instance_c14_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c14m14___ne__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c14m14] Failed to create thread for __ne__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c14m14___ne__(target_func=target_func):
            print("Starting async task: async_call_c14m14___ne__", file=stderr)
            time.sleep(0.000321) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c14m14] Exception in async task async_call_c14m14___ne__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c14m14___ne__", file=stderr)
        fuzzer_async_tasks.append(async_call_c14m14___ne__)

    try:
        res_c14m15 = callMethod("c14m15", instance_c14_popen, "__ge__",
            FilenoBomb(),
        verbose=True)
    except Exception as _argexc_c14m15:
        print("[c14m15] call skipped (argument build failed):", repr(_argexc_c14m15), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c14_popen, '__ge__')
    except Exception as e_get_target_func:
        print(f"[c14m15] Failed to get attribute __ge__ from instance_c14_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(ReentrantClearList(),), name='c14m15___ge__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c14m15] Failed to create thread for __ge__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c14m15___ge__(target_func=target_func):
            print("Starting async task: async_call_c14m15___ge__", file=stderr)
            time.sleep(0.000516) # Small delay
            try:
                target_func(-93274)
            except Exception as e_async_call:
                print(f"[c14m15] Exception in async task async_call_c14m15___ge__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c14m15___ge__", file=stderr)
        fuzzer_async_tasks.append(async_call_c14m15___ge__)

    print(f"--- Finished fuzzing instance: instance_c14_popen ---", file=stderr)

    del instance_c14_popen # Cleanup instance
    print("[c14] -explicit garbage collection for class instance-", file=stderr)
    collect()

print("[c15] Attempting to instantiate class: Popen", file=stderr)
instance_c15_popen = None # Initialize instance variable
try:
    instance_c15_popen = callFunc('c15_init', 'Popen',
        RaisingInstanceCheckType,
      )
except Exception as e_instantiate:
    instance_c15_popen = None
    print("[c15] Failed to instantiate Popen: {e_instantiate.__class__.__name__} {e_instantiate}", file=stderr)
    instance_c15_popen = None

try:
    print(f"--- (Depth 0) Dispatching Fuzz for: {instance_c15_popen!r} (hint: Popen, prefix: c15_popen_ops) ---", file=stderr)
except Exception as e:
    print(f"--- (Depth 0) Error calling repr() prefix: c15_popen_ops) ---", file=stderr)
if instance_c15_popen is not None:
    if skip_trivial_type(instance_c15_popen):
        print(f'Skipping deep diving on instance_c15_popen {type(instance_c15_popen)}', file=stderr)
    try:
        print(f'Instance {instance_c15_popen!r} (actual type {type(instance_c15_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    except Exception as e:
        print(f'Error printing instance repr() { e } (actual type {type(instance_c15_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    if skip_trivial_type(instance_c15_popen):
        print(f'Skipping deep diving on instance_c15_popen {type(instance_c15_popen)}', file=stderr)
    else:
        print(f'Instance instance_c15_popen (type {type(instance_c15_popen).__name__}) has no specific fuzzer, doing generic calls.', file=stderr)
        c15_popen_ops_generic_methods = []
        try:
            for c15_popen_ops_generic_attr_name in dir(instance_c15_popen):
                if c15_popen_ops_generic_attr_name.startswith('_'): continue
                try:
                    c15_popen_ops_generic_attr_val = getattr(instance_c15_popen, c15_popen_ops_generic_attr_name)
                    if callable(c15_popen_ops_generic_attr_val) and c15_popen_ops_generic_attr_name not in _FUSIL_METHOD_BLACKLIST: c15_popen_ops_generic_methods.append((c15_popen_ops_generic_attr_name, c15_popen_ops_generic_attr_val))
                except Exception: pass
        except Exception: c15_popen_ops_generic_methods = [] # Failed to get methods
        if c15_popen_ops_generic_methods:
            print(f'Found {len(c15_popen_ops_generic_methods)} callable methods for generic fuzzing of instance_c15_popen', file=stderr)
            for _i_c15_popen_ops_generic in range(min(len(c15_popen_ops_generic_methods), 15)):
                c15_popen_ops_generic_method_name_to_call, c15_popen_ops_generic_method_obj_to_call = choice(c15_popen_ops_generic_methods)
                # Conceptual call to generic method fuzzer
                if c15_popen_ops_generic_method_name_to_call not in _FUSIL_METHOD_BLACKLIST: callMethod(f'c15_popen_ops_generic_gen{_i_c15_popen_ops_generic}', instance_c15_popen, c15_popen_ops_generic_method_name_to_call)

if instance_c15_popen is not None and instance_c15_popen is not SENTINEL_VALUE:
    print(f"--- Fuzzing instance: instance_c15_popen (type hint: Popen, prefix: c15m) ---", file=stderr)
    if skip_trivial_type(instance_c15_popen):
        print(f'Skipping deep diving on instance_c15_popen {type(instance_c15_popen)}', file=stderr)
    # General method fuzzing for instance_c15_popen
    try:
        res_c15m1 = callMethod("c15m1", instance_c15_popen, "__getstate__",
        verbose=True)
    except Exception as _argexc_c15m1:
        print("[c15m1] call skipped (argument build failed):", repr(_argexc_c15m1), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c15_popen, '__getstate__')
    except Exception as e_get_target_func:
        print(f"[c15m1] Failed to get attribute __getstate__ from instance_c15_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c15m1___getstate__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c15m1] Failed to create thread for __getstate__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c15m1___getstate__(target_func=target_func):
            print("Starting async task: async_call_c15m1___getstate__", file=stderr)
            time.sleep(0.000046) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c15m1] Exception in async task async_call_c15m1___getstate__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c15m1___getstate__", file=stderr)
        fuzzer_async_tasks.append(async_call_c15m1___getstate__)

    try:
        res_c15m2 = callMethod("c15m2", instance_c15_popen, "terminate",
        verbose=True)
    except Exception as _argexc_c15m2:
        print("[c15m2] call skipped (argument build failed):", repr(_argexc_c15m2), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c15_popen, 'terminate')
    except Exception as e_get_target_func:
        print(f"[c15m2] Failed to get attribute terminate from instance_c15_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c15m2_terminate')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c15m2] Failed to create thread for terminate: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c15m2_terminate(target_func=target_func):
            print("Starting async task: async_call_c15m2_terminate", file=stderr)
            time.sleep(0.000003) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c15m2] Exception in async task async_call_c15m2_terminate: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c15m2_terminate", file=stderr)
        fuzzer_async_tasks.append(async_call_c15m2_terminate)

    try:
        res_c15m3 = callMethod("c15m3", instance_c15_popen, "_send_signal",
            HashBomb(),
        verbose=True)
    except Exception as _argexc_c15m3:
        print("[c15m3] call skipped (argument build failed):", repr(_argexc_c15m3), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c15_popen, '_send_signal')
    except Exception as e_get_target_func:
        print(f"[c15m3] Failed to get attribute _send_signal from instance_c15_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(errback,), name='c15m3__send_signal')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c15m3] Failed to create thread for _send_signal: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c15m3__send_signal(target_func=target_func):
            print("Starting async task: async_call_c15m3__send_signal", file=stderr)
            time.sleep(0.000768) # Small delay
            try:
                target_func(bytearray(b"abc\xe9\xff"))
            except Exception as e_async_call:
                print(f"[c15m3] Exception in async task async_call_c15m3__send_signal: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c15m3__send_signal", file=stderr)
        fuzzer_async_tasks.append(async_call_c15m3__send_signal)

    try:
        res_c15m4 = callMethod("c15m4", instance_c15_popen, "__le__",
            type,
        verbose=True)
    except Exception as _argexc_c15m4:
        print("[c15m4] call skipped (argument build failed):", repr(_argexc_c15m4), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c15_popen, '__le__')
    except Exception as e_get_target_func:
        print(f"[c15m4] Failed to get attribute __le__ from instance_c15_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(LyingInplace(),), name='c15m4___le__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c15m4] Failed to create thread for __le__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c15m4___le__(target_func=target_func):
            print("Starting async task: async_call_c15m4___le__", file=stderr)
            time.sleep(0.000985) # Small delay
            try:
                target_func((lambda x: sys.maxsize))
            except Exception as e_async_call:
                print(f"[c15m4] Exception in async task async_call_c15m4___le__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c15m4___le__", file=stderr)
        fuzzer_async_tasks.append(async_call_c15m4___le__)

    try:
        res_c15m5 = callMethod("c15m5", instance_c15_popen, "__getattribute__",
            EqBomb(),
        verbose=True)
    except Exception as _argexc_c15m5:
        print("[c15m5] call skipped (argument build failed):", repr(_argexc_c15m5), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c15_popen, '__getattribute__')
    except Exception as e_get_target_func:
        print(f"[c15m5] Failed to get attribute __getattribute__ from instance_c15_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(ReadBomb(),), name='c15m5___getattribute__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c15m5] Failed to create thread for __getattribute__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c15m5___getattribute__(target_func=target_func):
            print("Starting async task: async_call_c15m5___getattribute__", file=stderr)
            time.sleep(0.000626) # Small delay
            try:
                target_func(WrongTypeFile())
            except Exception as e_async_call:
                print(f"[c15m5] Exception in async task async_call_c15m5___getattribute__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c15m5___getattribute__", file=stderr)
        fuzzer_async_tasks.append(async_call_c15m5___getattribute__)

    try:
        res_c15m6 = callMethod("c15m6", instance_c15_popen, "__repr__",
        verbose=True)
    except Exception as _argexc_c15m6:
        print("[c15m6] call skipped (argument build failed):", repr(_argexc_c15m6), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c15_popen, '__repr__')
    except Exception as e_get_target_func:
        print(f"[c15m6] Failed to get attribute __repr__ from instance_c15_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c15m6___repr__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c15m6] Failed to create thread for __repr__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c15m6___repr__(target_func=target_func):
            print("Starting async task: async_call_c15m6___repr__", file=stderr)
            time.sleep(0.000707) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c15m6] Exception in async task async_call_c15m6___repr__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c15m6___repr__", file=stderr)
        fuzzer_async_tasks.append(async_call_c15m6___repr__)

    try:
        res_c15m7 = callMethod("c15m7", instance_c15_popen, "__ne__",
            r"VS.aKLqeT.",
            type,
        verbose=True)
    except Exception as _argexc_c15m7:
        print("[c15m7] call skipped (argument build failed):", repr(_argexc_c15m7), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c15_popen, '__ne__')
    except Exception as e_get_target_func:
        print(f"[c15m7] Failed to get attribute __ne__ from instance_c15_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(errback, b"\xE6\xCC\x08\xDF\xA7\xA6\x59\xFF\x6A"), name='c15m7___ne__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c15m7] Failed to create thread for __ne__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c15m7___ne__(target_func=target_func):
            print("Starting async task: async_call_c15m7___ne__", file=stderr)
            time.sleep(0.000355) # Small delay
            try:
                target_func(LyingInstanceCheckType, '/tmp/fusil-fixtures/fusil_fixture.txt')
            except Exception as e_async_call:
                print(f"[c15m7] Exception in async task async_call_c15m7___ne__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c15m7___ne__", file=stderr)
        fuzzer_async_tasks.append(async_call_c15m7___ne__)

    try:
        res_c15m8 = callMethod("c15m8", instance_c15_popen, "_launch",
            HashBomb(),
        verbose=True)
    except Exception as _argexc_c15m8:
        print("[c15m8] call skipped (argument build failed):", repr(_argexc_c15m8), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c15_popen, '_launch')
    except Exception as e_get_target_func:
        print(f"[c15m8] Failed to get attribute _launch from instance_c15_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("A" * (2 ** 16),), name='c15m8__launch')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c15m8] Failed to create thread for _launch: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c15m8__launch(target_func=target_func):
            print("Starting async task: async_call_c15m8__launch", file=stderr)
            time.sleep(0.000170) # Small delay
            try:
                target_func(8)
            except Exception as e_async_call:
                print(f"[c15m8] Exception in async task async_call_c15m8__launch: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c15m8__launch", file=stderr)
        fuzzer_async_tasks.append(async_call_c15m8__launch)

    try:
        res_c15m9 = callMethod("c15m9", instance_c15_popen, "__reduce_ex__",
            weird_classes['weird_tuple'],
            ReentrantClearList(),
        verbose=True)
    except Exception as _argexc_c15m9:
        print("[c15m9] call skipped (argument build failed):", repr(_argexc_c15m9), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c15_popen, '__reduce_ex__')
    except Exception as e_get_target_func:
        print(f"[c15m9] Failed to get attribute __reduce_ex__ from instance_c15_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(bytearray(b"abc\xe9\xff"), IndexBomb()), name='c15m9___reduce_ex__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c15m9] Failed to create thread for __reduce_ex__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c15m9___reduce_ex__(target_func=target_func):
            print("Starting async task: async_call_c15m9___reduce_ex__", file=stderr)
            time.sleep(0.000884) # Small delay
            try:
                target_func(FilenoBomb(), "\U0010FFFF")
            except Exception as e_async_call:
                print(f"[c15m9] Exception in async task async_call_c15m9___reduce_ex__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c15m9___reduce_ex__", file=stderr)
        fuzzer_async_tasks.append(async_call_c15m9___reduce_ex__)

    try:
        res_c15m10 = callMethod("c15m10", instance_c15_popen, "close",
        verbose=True)
    except Exception as _argexc_c15m10:
        print("[c15m10] call skipped (argument build failed):", repr(_argexc_c15m10), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c15_popen, 'close')
    except Exception as e_get_target_func:
        print(f"[c15m10] Failed to get attribute close from instance_c15_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c15m10_close')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c15m10] Failed to create thread for close: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c15m10_close(target_func=target_func):
            print("Starting async task: async_call_c15m10_close", file=stderr)
            time.sleep(0.000458) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c15m10] Exception in async task async_call_c15m10_close: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c15m10_close", file=stderr)
        fuzzer_async_tasks.append(async_call_c15m10_close)

    try:
        res_c15m11 = callMethod("c15m11", instance_c15_popen, "__reduce__",
        verbose=True)
    except Exception as _argexc_c15m11:
        print("[c15m11] call skipped (argument build failed):", repr(_argexc_c15m11), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c15_popen, '__reduce__')
    except Exception as e_get_target_func:
        print(f"[c15m11] Failed to get attribute __reduce__ from instance_c15_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c15m11___reduce__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c15m11] Failed to create thread for __reduce__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c15m11___reduce__(target_func=target_func):
            print("Starting async task: async_call_c15m11___reduce__", file=stderr)
            time.sleep(0.000688) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c15m11] Exception in async task async_call_c15m11___reduce__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c15m11___reduce__", file=stderr)
        fuzzer_async_tasks.append(async_call_c15m11___reduce__)

    try:
        res_c15m12 = callMethod("c15m12", instance_c15_popen, "terminate",
            HiddenNameType,
        verbose=True)
    except Exception as _argexc_c15m12:
        print("[c15m12] call skipped (argument build failed):", repr(_argexc_c15m12), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c15_popen, 'terminate')
    except Exception as e_get_target_func:
        print(f"[c15m12] Failed to get attribute terminate from instance_c15_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("\u6A7A\u637E\u930C\u1E0D\uFA7A\u4E4F\uF2D6\u2833",), name='c15m12_terminate')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c15m12] Failed to create thread for terminate: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c15m12_terminate(target_func=target_func):
            print("Starting async task: async_call_c15m12_terminate", file=stderr)
            time.sleep(0.000961) # Small delay
            try:
                target_func(Exception('fuzzer_generated_exception'))
            except Exception as e_async_call:
                print(f"[c15m12] Exception in async task async_call_c15m12_terminate: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c15m12_terminate", file=stderr)
        fuzzer_async_tasks.append(async_call_c15m12_terminate)

    try:
        res_c15m13 = callMethod("c15m13", instance_c15_popen, "__repr__",
            "\x00",
        verbose=True)
    except Exception as _argexc_c15m13:
        print("[c15m13] call skipped (argument build failed):", repr(_argexc_c15m13), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c15_popen, '__repr__')
    except Exception as e_get_target_func:
        print(f"[c15m13] Failed to get attribute __repr__ from instance_c15_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(-17,), name='c15m13___repr__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c15m13] Failed to create thread for __repr__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c15m13___repr__(target_func=target_func):
            print("Starting async task: async_call_c15m13___repr__", file=stderr)
            time.sleep(0.000856) # Small delay
            try:
                target_func(object())
            except Exception as e_async_call:
                print(f"[c15m13] Exception in async task async_call_c15m13___repr__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c15m13___repr__", file=stderr)
        fuzzer_async_tasks.append(async_call_c15m13___repr__)

    try:
        res_c15m14 = callMethod("c15m14", instance_c15_popen, "__ne__",
        verbose=True)
    except Exception as _argexc_c15m14:
        print("[c15m14] call skipped (argument build failed):", repr(_argexc_c15m14), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c15_popen, '__ne__')
    except Exception as e_get_target_func:
        print(f"[c15m14] Failed to get attribute __ne__ from instance_c15_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c15m14___ne__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c15m14] Failed to create thread for __ne__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c15m14___ne__(target_func=target_func):
            print("Starting async task: async_call_c15m14___ne__", file=stderr)
            time.sleep(0.000717) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c15m14] Exception in async task async_call_c15m14___ne__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c15m14___ne__", file=stderr)
        fuzzer_async_tasks.append(async_call_c15m14___ne__)

    try:
        res_c15m15 = callMethod("c15m15", instance_c15_popen, "__setattr__",
            "\uDC80",
            tuple[weird_classes['weird_Decimal']] | weird_classes['weird_OrderedDict'] | big_union,
        verbose=True)
    except Exception as _argexc_c15m15:
        print("[c15m15] call skipped (argument build failed):", repr(_argexc_c15m15), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c15_popen, '__setattr__')
    except Exception as e_get_target_func:
        print(f"[c15m15] Failed to get attribute __setattr__ from instance_c15_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(b"\x2B\xD6\x69\x4E", MagicMock()), name='c15m15___setattr__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c15m15] Failed to create thread for __setattr__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c15m15___setattr__(target_func=target_func):
            print("Starting async task: async_call_c15m15___setattr__", file=stderr)
            time.sleep(0.000467) # Small delay
            try:
                target_func(dict[weird_classes['weird_tuple']], liar1)
            except Exception as e_async_call:
                print(f"[c15m15] Exception in async task async_call_c15m15___setattr__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c15m15___setattr__", file=stderr)
        fuzzer_async_tasks.append(async_call_c15m15___setattr__)

    print(f"--- Finished fuzzing instance: instance_c15_popen ---", file=stderr)

    del instance_c15_popen # Cleanup instance
    print("[c15] -explicit garbage collection for class instance-", file=stderr)
    collect()

print("[c16] Attempting to instantiate class: Popen", file=stderr)
instance_c16_popen = None # Initialize instance variable
try:
    instance_c16_popen = callFunc('c16_init', 'Popen',
        (sys.maxunicode + 1,),
      )
except Exception as e_instantiate:
    instance_c16_popen = None
    print("[c16] Failed to instantiate Popen: {e_instantiate.__class__.__name__} {e_instantiate}", file=stderr)
    instance_c16_popen = None

try:
    print(f"--- (Depth 0) Dispatching Fuzz for: {instance_c16_popen!r} (hint: Popen, prefix: c16_popen_ops) ---", file=stderr)
except Exception as e:
    print(f"--- (Depth 0) Error calling repr() prefix: c16_popen_ops) ---", file=stderr)
if instance_c16_popen is not None:
    if skip_trivial_type(instance_c16_popen):
        print(f'Skipping deep diving on instance_c16_popen {type(instance_c16_popen)}', file=stderr)
    try:
        print(f'Instance {instance_c16_popen!r} (actual type {type(instance_c16_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    except Exception as e:
        print(f'Error printing instance repr() { e } (actual type {type(instance_c16_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    if skip_trivial_type(instance_c16_popen):
        print(f'Skipping deep diving on instance_c16_popen {type(instance_c16_popen)}', file=stderr)
    else:
        print(f'Instance instance_c16_popen (type {type(instance_c16_popen).__name__}) has no specific fuzzer, doing generic calls.', file=stderr)
        c16_popen_ops_generic_methods = []
        try:
            for c16_popen_ops_generic_attr_name in dir(instance_c16_popen):
                if c16_popen_ops_generic_attr_name.startswith('_'): continue
                try:
                    c16_popen_ops_generic_attr_val = getattr(instance_c16_popen, c16_popen_ops_generic_attr_name)
                    if callable(c16_popen_ops_generic_attr_val) and c16_popen_ops_generic_attr_name not in _FUSIL_METHOD_BLACKLIST: c16_popen_ops_generic_methods.append((c16_popen_ops_generic_attr_name, c16_popen_ops_generic_attr_val))
                except Exception: pass
        except Exception: c16_popen_ops_generic_methods = [] # Failed to get methods
        if c16_popen_ops_generic_methods:
            print(f'Found {len(c16_popen_ops_generic_methods)} callable methods for generic fuzzing of instance_c16_popen', file=stderr)
            for _i_c16_popen_ops_generic in range(min(len(c16_popen_ops_generic_methods), 15)):
                c16_popen_ops_generic_method_name_to_call, c16_popen_ops_generic_method_obj_to_call = choice(c16_popen_ops_generic_methods)
                # Conceptual call to generic method fuzzer
                if c16_popen_ops_generic_method_name_to_call not in _FUSIL_METHOD_BLACKLIST: callMethod(f'c16_popen_ops_generic_gen{_i_c16_popen_ops_generic}', instance_c16_popen, c16_popen_ops_generic_method_name_to_call)

if instance_c16_popen is not None and instance_c16_popen is not SENTINEL_VALUE:
    print(f"--- Fuzzing instance: instance_c16_popen (type hint: Popen, prefix: c16m) ---", file=stderr)
    if skip_trivial_type(instance_c16_popen):
        print(f'Skipping deep diving on instance_c16_popen {type(instance_c16_popen)}', file=stderr)
    # General method fuzzing for instance_c16_popen
    try:
        res_c16m1 = callMethod("c16m1", instance_c16_popen, "kill",
        verbose=True)
    except Exception as _argexc_c16m1:
        print("[c16m1] call skipped (argument build failed):", repr(_argexc_c16m1), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c16_popen, 'kill')
    except Exception as e_get_target_func:
        print(f"[c16m1] Failed to get attribute kill from instance_c16_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c16m1_kill')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c16m1] Failed to create thread for kill: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c16m1_kill(target_func=target_func):
            print("Starting async task: async_call_c16m1_kill", file=stderr)
            time.sleep(0.000030) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c16m1] Exception in async task async_call_c16m1_kill: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c16m1_kill", file=stderr)
        fuzzer_async_tasks.append(async_call_c16m1_kill)

    try:
        res_c16m2 = callMethod("c16m2", instance_c16_popen, "__ne__",
            "d\x0E",
        verbose=True)
    except Exception as _argexc_c16m2:
        print("[c16m2] call skipped (argument build failed):", repr(_argexc_c16m2), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c16_popen, '__ne__')
    except Exception as e_get_target_func:
        print(f"[c16m2] Failed to get attribute __ne__ from instance_c16_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(tricky_capsule,), name='c16m2___ne__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c16m2] Failed to create thread for __ne__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c16m2___ne__(target_func=target_func):
            print("Starting async task: async_call_c16m2___ne__", file=stderr)
            time.sleep(0.000402) # Small delay
            try:
                target_func(Exception('fuzzer_generated_exception'))
            except Exception as e_async_call:
                print(f"[c16m2] Exception in async task async_call_c16m2___ne__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c16m2___ne__", file=stderr)
        fuzzer_async_tasks.append(async_call_c16m2___ne__)

    try:
        res_c16m3 = callMethod("c16m3", instance_c16_popen, "poll",
            MutatingIterable(),
        verbose=True)
    except Exception as _argexc_c16m3:
        print("[c16m3] call skipped (argument build failed):", repr(_argexc_c16m3), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c16_popen, 'poll')
    except Exception as e_get_target_func:
        print(f"[c16m3] Failed to get attribute poll from instance_c16_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(weird_classes['weird_Decimal'],), name='c16m3_poll')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c16m3] Failed to create thread for poll: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c16m3_poll(target_func=target_func):
            print("Starting async task: async_call_c16m3_poll", file=stderr)
            time.sleep(0.000298) # Small delay
            try:
                target_func("d_\x0D\x12\xEB\xA0\xE7\xD4/F+\xA5\x1B\x9C\x91\x99\xF4")
            except Exception as e_async_call:
                print(f"[c16m3] Exception in async task async_call_c16m3_poll: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c16m3_poll", file=stderr)
        fuzzer_async_tasks.append(async_call_c16m3_poll)

    try:
        res_c16m4 = callMethod("c16m4", instance_c16_popen, "__subclasshook__",
            LyingLen(),
        verbose=True)
    except Exception as _argexc_c16m4:
        print("[c16m4] call skipped (argument build failed):", repr(_argexc_c16m4), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c16_popen, '__subclasshook__')
    except Exception as e_get_target_func:
        print(f"[c16m4] Failed to get attribute __subclasshook__ from instance_c16_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(errback,), name='c16m4___subclasshook__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c16m4] Failed to create thread for __subclasshook__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c16m4___subclasshook__(target_func=target_func):
            print("Starting async task: async_call_c16m4___subclasshook__", file=stderr)
            time.sleep(0.000550) # Small delay
            try:
                target_func(354.3)
            except Exception as e_async_call:
                print(f"[c16m4] Exception in async task async_call_c16m4___subclasshook__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c16m4___subclasshook__", file=stderr)
        fuzzer_async_tasks.append(async_call_c16m4___subclasshook__)

    try:
        res_c16m5 = callMethod("c16m5", instance_c16_popen, "__hash__",
        verbose=True)
    except Exception as _argexc_c16m5:
        print("[c16m5] call skipped (argument build failed):", repr(_argexc_c16m5), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c16_popen, '__hash__')
    except Exception as e_get_target_func:
        print(f"[c16m5] Failed to get attribute __hash__ from instance_c16_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c16m5___hash__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c16m5] Failed to create thread for __hash__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c16m5___hash__(target_func=target_func):
            print("Starting async task: async_call_c16m5___hash__", file=stderr)
            time.sleep(0.000964) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c16m5] Exception in async task async_call_c16m5___hash__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c16m5___hash__", file=stderr)
        fuzzer_async_tasks.append(async_call_c16m5___hash__)

    try:
        res_c16m6 = callMethod("c16m6", instance_c16_popen, "__eq__",
            tuple[weird_classes['weird_int']],
        verbose=True)
    except Exception as _argexc_c16m6:
        print("[c16m6] call skipped (argument build failed):", repr(_argexc_c16m6), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c16_popen, '__eq__')
    except Exception as e_get_target_func:
        print(f"[c16m6] Failed to get attribute __eq__ from instance_c16_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(b"",), name='c16m6___eq__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c16m6] Failed to create thread for __eq__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c16m6___eq__(target_func=target_func):
            print("Starting async task: async_call_c16m6___eq__", file=stderr)
            time.sleep(0.000822) # Small delay
            try:
                target_func(b"\x3D\x42\x8A\x8D\xDA\x94\x41\x33\x0E\x51\xBD\x0F\x12\xD4\x2F")
            except Exception as e_async_call:
                print(f"[c16m6] Exception in async task async_call_c16m6___eq__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c16m6___eq__", file=stderr)
        fuzzer_async_tasks.append(async_call_c16m6___eq__)

    try:
        res_c16m7 = callMethod("c16m7", instance_c16_popen, "__str__",
        verbose=True)
    except Exception as _argexc_c16m7:
        print("[c16m7] call skipped (argument build failed):", repr(_argexc_c16m7), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c16_popen, '__str__')
    except Exception as e_get_target_func:
        print(f"[c16m7] Failed to get attribute __str__ from instance_c16_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c16m7___str__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c16m7] Failed to create thread for __str__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c16m7___str__(target_func=target_func):
            print("Starting async task: async_call_c16m7___str__", file=stderr)
            time.sleep(0.000662) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c16m7] Exception in async task async_call_c16m7___str__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c16m7___str__", file=stderr)
        fuzzer_async_tasks.append(async_call_c16m7___str__)

    try:
        res_c16m8 = callMethod("c16m8", instance_c16_popen, "__ne__",
            "[`\xB6}%\x96\xB1\x84\xC2\xA2T\x18\x08",
        verbose=True)
    except Exception as _argexc_c16m8:
        print("[c16m8] call skipped (argument build failed):", repr(_argexc_c16m8), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c16_popen, '__ne__')
    except Exception as e_get_target_func:
        print(f"[c16m8] Failed to get attribute __ne__ from instance_c16_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(TypeFlipIterator(),), name='c16m8___ne__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c16m8] Failed to create thread for __ne__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c16m8___ne__(target_func=target_func):
            print("Starting async task: async_call_c16m8___ne__", file=stderr)
            time.sleep(0.000308) # Small delay
            try:
                target_func(weird_instances['weird_set_special'])
            except Exception as e_async_call:
                print(f"[c16m8] Exception in async task async_call_c16m8___ne__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c16m8___ne__", file=stderr)
        fuzzer_async_tasks.append(async_call_c16m8___ne__)

    try:
        res_c16m9 = callMethod("c16m9", instance_c16_popen, "__hash__",
        verbose=True)
    except Exception as _argexc_c16m9:
        print("[c16m9] call skipped (argument build failed):", repr(_argexc_c16m9), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c16_popen, '__hash__')
    except Exception as e_get_target_func:
        print(f"[c16m9] Failed to get attribute __hash__ from instance_c16_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c16m9___hash__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c16m9] Failed to create thread for __hash__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c16m9___hash__(target_func=target_func):
            print("Starting async task: async_call_c16m9___hash__", file=stderr)
            time.sleep(0.000001) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c16m9] Exception in async task async_call_c16m9___hash__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c16m9___hash__", file=stderr)
        fuzzer_async_tasks.append(async_call_c16m9___hash__)

    try:
        res_c16m10 = callMethod("c16m10", instance_c16_popen, "__subclasshook__",
            DescriptorBomb(),
        verbose=True)
    except Exception as _argexc_c16m10:
        print("[c16m10] call skipped (argument build failed):", repr(_argexc_c16m10), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c16_popen, '__subclasshook__')
    except Exception as e_get_target_func:
        print(f"[c16m10] Failed to get attribute __subclasshook__ from instance_c16_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(r"vG\AL\Dh\B.ne+\D\BS.CXp..KJaypn\Z?BS\A+",), name='c16m10___subclasshook__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c16m10] Failed to create thread for __subclasshook__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c16m10___subclasshook__(target_func=target_func):
            print("Starting async task: async_call_c16m10___subclasshook__", file=stderr)
            time.sleep(0.000849) # Small delay
            try:
                target_func('/tmp/fusil-fixtures/fusil_fixture.txt')
            except Exception as e_async_call:
                print(f"[c16m10] Exception in async task async_call_c16m10___subclasshook__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c16m10___subclasshook__", file=stderr)
        fuzzer_async_tasks.append(async_call_c16m10___subclasshook__)

    try:
        res_c16m11 = callMethod("c16m11", instance_c16_popen, "__format__",
            weird_instances['weird_complex_2**63'],
        verbose=True)
    except Exception as _argexc_c16m11:
        print("[c16m11] call skipped (argument build failed):", repr(_argexc_c16m11), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c16_popen, '__format__')
    except Exception as e_get_target_func:
        print(f"[c16m11] Failed to get attribute __format__ from instance_c16_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("9\x11\x85\xA9\xDF,",), name='c16m11___format__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c16m11] Failed to create thread for __format__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c16m11___format__(target_func=target_func):
            print("Starting async task: async_call_c16m11___format__", file=stderr)
            time.sleep(0.000023) # Small delay
            try:
                target_func(66.74)
            except Exception as e_async_call:
                print(f"[c16m11] Exception in async task async_call_c16m11___format__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c16m11___format__", file=stderr)
        fuzzer_async_tasks.append(async_call_c16m11___format__)

    try:
        res_c16m12 = callMethod("c16m12", instance_c16_popen, "_launch",
            LyingLen(),
        verbose=True)
    except Exception as _argexc_c16m12:
        print("[c16m12] call skipped (argument build failed):", repr(_argexc_c16m12), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c16_popen, '_launch')
    except Exception as e_get_target_func:
        print(f"[c16m12] Failed to get attribute _launch from instance_c16_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(weird_classes['weird_Counter'],), name='c16m12__launch')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c16m12] Failed to create thread for _launch: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c16m12__launch(target_func=target_func):
            print("Starting async task: async_call_c16m12__launch", file=stderr)
            time.sleep(0.000485) # Small delay
            try:
                target_func('/tmp/fusil-fixtures/fusil_fixture.txt')
            except Exception as e_async_call:
                print(f"[c16m12] Exception in async task async_call_c16m12__launch: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c16m12__launch", file=stderr)
        fuzzer_async_tasks.append(async_call_c16m12__launch)

    try:
        res_c16m13 = callMethod("c16m13", instance_c16_popen, "__ge__",
            "\u1E60\u2D00\u032D\u456C\u9712\uEF29\uAFDD\u780C\uE11D\uF68A\u9D57\uA068\u70E9",
        verbose=True)
    except Exception as _argexc_c16m13:
        print("[c16m13] call skipped (argument build failed):", repr(_argexc_c16m13), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c16_popen, '__ge__')
    except Exception as e_get_target_func:
        print(f"[c16m13] Failed to get attribute __ge__ from instance_c16_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(6175524519476758,), name='c16m13___ge__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c16m13] Failed to create thread for __ge__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c16m13___ge__(target_func=target_func):
            print("Starting async task: async_call_c16m13___ge__", file=stderr)
            time.sleep(0.000731) # Small delay
            try:
                target_func("rO0QV3qNxFrV14zaqIERVzb5VBQVmwVqxl/8zbnrOGYqvI/NWnJHblo_q6h2iNmg/ir//N")
            except Exception as e_async_call:
                print(f"[c16m13] Exception in async task async_call_c16m13___ge__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c16m13___ge__", file=stderr)
        fuzzer_async_tasks.append(async_call_c16m13___ge__)

    try:
        res_c16m14 = callMethod("c16m14", instance_c16_popen, "__le__",
            weird_classes['weird_Counter'],
        verbose=True)
    except Exception as _argexc_c16m14:
        print("[c16m14] call skipped (argument build failed):", repr(_argexc_c16m14), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c16_popen, '__le__')
    except Exception as e_get_target_func:
        print(f"[c16m14] Failed to get attribute __le__ from instance_c16_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("\x00",), name='c16m14___le__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c16m14] Failed to create thread for __le__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c16m14___le__(target_func=target_func):
            print("Starting async task: async_call_c16m14___le__", file=stderr)
            time.sleep(0.000023) # Small delay
            try:
                target_func(2720)
            except Exception as e_async_call:
                print(f"[c16m14] Exception in async task async_call_c16m14___le__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c16m14___le__", file=stderr)
        fuzzer_async_tasks.append(async_call_c16m14___le__)

    try:
        res_c16m15 = callMethod("c16m15", instance_c16_popen, "__init_subclass__",
            "\u0C6B\uF3F4\u55E1\u751E\u1BA1\uC692\u8CF4\u1A53\uC87E\u86AB\uD884\u1879",
        verbose=True)
    except Exception as _argexc_c16m15:
        print("[c16m15] call skipped (argument build failed):", repr(_argexc_c16m15), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c16_popen, '__init_subclass__')
    except Exception as e_get_target_func:
        print(f"[c16m15] Failed to get attribute __init_subclass__ from instance_c16_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(-16,), name='c16m15___init_subclass__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c16m15] Failed to create thread for __init_subclass__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c16m15___init_subclass__(target_func=target_func):
            print("Starting async task: async_call_c16m15___init_subclass__", file=stderr)
            time.sleep(0.000034) # Small delay
            try:
                target_func(LyingLen())
            except Exception as e_async_call:
                print(f"[c16m15] Exception in async task async_call_c16m15___init_subclass__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c16m15___init_subclass__", file=stderr)
        fuzzer_async_tasks.append(async_call_c16m15___init_subclass__)

    print(f"--- Finished fuzzing instance: instance_c16_popen ---", file=stderr)

    del instance_c16_popen # Cleanup instance
    print("[c16] -explicit garbage collection for class instance-", file=stderr)
    collect()

print("[c17] Attempting to instantiate class: Popen", file=stderr)
instance_c17_popen = None # Initialize instance variable
try:
    instance_c17_popen = callFunc('c17_init', 'Popen',
        dict[weird_classes['weird_Decimal']],
      )
except Exception as e_instantiate:
    instance_c17_popen = None
    print("[c17] Failed to instantiate Popen: {e_instantiate.__class__.__name__} {e_instantiate}", file=stderr)
    instance_c17_popen = None

try:
    print(f"--- (Depth 0) Dispatching Fuzz for: {instance_c17_popen!r} (hint: Popen, prefix: c17_popen_ops) ---", file=stderr)
except Exception as e:
    print(f"--- (Depth 0) Error calling repr() prefix: c17_popen_ops) ---", file=stderr)
if instance_c17_popen is not None:
    if skip_trivial_type(instance_c17_popen):
        print(f'Skipping deep diving on instance_c17_popen {type(instance_c17_popen)}', file=stderr)
    try:
        print(f'Instance {instance_c17_popen!r} (actual type {type(instance_c17_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    except Exception as e:
        print(f'Error printing instance repr() { e } (actual type {type(instance_c17_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    if skip_trivial_type(instance_c17_popen):
        print(f'Skipping deep diving on instance_c17_popen {type(instance_c17_popen)}', file=stderr)
    else:
        print(f'Instance instance_c17_popen (type {type(instance_c17_popen).__name__}) has no specific fuzzer, doing generic calls.', file=stderr)
        c17_popen_ops_generic_methods = []
        try:
            for c17_popen_ops_generic_attr_name in dir(instance_c17_popen):
                if c17_popen_ops_generic_attr_name.startswith('_'): continue
                try:
                    c17_popen_ops_generic_attr_val = getattr(instance_c17_popen, c17_popen_ops_generic_attr_name)
                    if callable(c17_popen_ops_generic_attr_val) and c17_popen_ops_generic_attr_name not in _FUSIL_METHOD_BLACKLIST: c17_popen_ops_generic_methods.append((c17_popen_ops_generic_attr_name, c17_popen_ops_generic_attr_val))
                except Exception: pass
        except Exception: c17_popen_ops_generic_methods = [] # Failed to get methods
        if c17_popen_ops_generic_methods:
            print(f'Found {len(c17_popen_ops_generic_methods)} callable methods for generic fuzzing of instance_c17_popen', file=stderr)
            for _i_c17_popen_ops_generic in range(min(len(c17_popen_ops_generic_methods), 15)):
                c17_popen_ops_generic_method_name_to_call, c17_popen_ops_generic_method_obj_to_call = choice(c17_popen_ops_generic_methods)
                # Conceptual call to generic method fuzzer
                if c17_popen_ops_generic_method_name_to_call not in _FUSIL_METHOD_BLACKLIST: callMethod(f'c17_popen_ops_generic_gen{_i_c17_popen_ops_generic}', instance_c17_popen, c17_popen_ops_generic_method_name_to_call)

if instance_c17_popen is not None and instance_c17_popen is not SENTINEL_VALUE:
    print(f"--- Fuzzing instance: instance_c17_popen (type hint: Popen, prefix: c17m) ---", file=stderr)
    if skip_trivial_type(instance_c17_popen):
        print(f'Skipping deep diving on instance_c17_popen {type(instance_c17_popen)}', file=stderr)
    # General method fuzzing for instance_c17_popen
    try:
        res_c17m1 = callMethod("c17m1", instance_c17_popen, "__reduce__",
        verbose=True)
    except Exception as _argexc_c17m1:
        print("[c17m1] call skipped (argument build failed):", repr(_argexc_c17m1), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c17_popen, '__reduce__')
    except Exception as e_get_target_func:
        print(f"[c17m1] Failed to get attribute __reduce__ from instance_c17_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c17m1___reduce__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c17m1] Failed to create thread for __reduce__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c17m1___reduce__(target_func=target_func):
            print("Starting async task: async_call_c17m1___reduce__", file=stderr)
            time.sleep(0.000447) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c17m1] Exception in async task async_call_c17m1___reduce__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c17m1___reduce__", file=stderr)
        fuzzer_async_tasks.append(async_call_c17m1___reduce__)

    try:
        res_c17m2 = callMethod("c17m2", instance_c17_popen, "__reduce_ex__",
            [],
        verbose=True)
    except Exception as _argexc_c17m2:
        print("[c17m2] call skipped (argument build failed):", repr(_argexc_c17m2), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c17_popen, '__reduce_ex__')
    except Exception as e_get_target_func:
        print(f"[c17m2] Failed to get attribute __reduce_ex__ from instance_c17_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(weird_instances['weird_str_single'],), name='c17m2___reduce_ex__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c17m2] Failed to create thread for __reduce_ex__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c17m2___reduce_ex__(target_func=target_func):
            print("Starting async task: async_call_c17m2___reduce_ex__", file=stderr)
            time.sleep(0.000333) # Small delay
            try:
                target_func(LyingEq())
            except Exception as e_async_call:
                print(f"[c17m2] Exception in async task async_call_c17m2___reduce_ex__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c17m2___reduce_ex__", file=stderr)
        fuzzer_async_tasks.append(async_call_c17m2___reduce_ex__)

    try:
        res_c17m3 = callMethod("c17m3", instance_c17_popen, "__setattr__",
            HiddenNameType,
            -505.0,
        verbose=True)
    except Exception as _argexc_c17m3:
        print("[c17m3] call skipped (argument build failed):", repr(_argexc_c17m3), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c17_popen, '__setattr__')
    except Exception as e_get_target_func:
        print(f"[c17m3] Failed to get attribute __setattr__ from instance_c17_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(DescriptorBomb(), LyingInstanceCheckType), name='c17m3___setattr__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c17m3] Failed to create thread for __setattr__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c17m3___setattr__(target_func=target_func):
            print("Starting async task: async_call_c17m3___setattr__", file=stderr)
            time.sleep(0.000245) # Small delay
            try:
                target_func(False, SuperBomb())
            except Exception as e_async_call:
                print(f"[c17m3] Exception in async task async_call_c17m3___setattr__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c17m3___setattr__", file=stderr)
        fuzzer_async_tasks.append(async_call_c17m3___setattr__)

    try:
        res_c17m4 = callMethod("c17m4", instance_c17_popen, "__str__",
        verbose=True)
    except Exception as _argexc_c17m4:
        print("[c17m4] call skipped (argument build failed):", repr(_argexc_c17m4), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c17_popen, '__str__')
    except Exception as e_get_target_func:
        print(f"[c17m4] Failed to get attribute __str__ from instance_c17_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c17m4___str__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c17m4] Failed to create thread for __str__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c17m4___str__(target_func=target_func):
            print("Starting async task: async_call_c17m4___str__", file=stderr)
            time.sleep(0.000583) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c17m4] Exception in async task async_call_c17m4___str__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c17m4___str__", file=stderr)
        fuzzer_async_tasks.append(async_call_c17m4___str__)

    try:
        res_c17m5 = callMethod("c17m5", instance_c17_popen, "__getattribute__",
            dict[weird_classes['weird_Decimal']],
        verbose=True)
    except Exception as _argexc_c17m5:
        print("[c17m5] call skipped (argument build failed):", repr(_argexc_c17m5), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c17_popen, '__getattribute__')
    except Exception as e_get_target_func:
        print(f"[c17m5] Failed to get attribute __getattribute__ from instance_c17_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(-121,), name='c17m5___getattribute__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c17m5] Failed to create thread for __getattribute__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c17m5___getattribute__(target_func=target_func):
            print("Starting async task: async_call_c17m5___getattribute__", file=stderr)
            time.sleep(0.000669) # Small delay
            try:
                target_func(b"")
            except Exception as e_async_call:
                print(f"[c17m5] Exception in async task async_call_c17m5___getattribute__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c17m5___getattribute__", file=stderr)
        fuzzer_async_tasks.append(async_call_c17m5___getattribute__)

    try:
        res_c17m6 = callMethod("c17m6", instance_c17_popen, "poll",
            ReprBomb(),
        verbose=True)
    except Exception as _argexc_c17m6:
        print("[c17m6] call skipped (argument build failed):", repr(_argexc_c17m6), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c17_popen, 'poll')
    except Exception as e_get_target_func:
        print(f"[c17m6] Failed to get attribute poll from instance_c17_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(ReentrantClearDict(),), name='c17m6_poll')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c17m6] Failed to create thread for poll: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c17m6_poll(target_func=target_func):
            print("Starting async task: async_call_c17m6_poll", file=stderr)
            time.sleep(0.000020) # Small delay
            try:
                target_func(int)
            except Exception as e_async_call:
                print(f"[c17m6] Exception in async task async_call_c17m6_poll: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c17m6_poll", file=stderr)
        fuzzer_async_tasks.append(async_call_c17m6_poll)

    try:
        res_c17m7 = callMethod("c17m7", instance_c17_popen, "__format__",
            GrowingLen(),
        verbose=True)
    except Exception as _argexc_c17m7:
        print("[c17m7] call skipped (argument build failed):", repr(_argexc_c17m7), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c17_popen, '__format__')
    except Exception as e_get_target_func:
        print(f"[c17m7] Failed to get attribute __format__ from instance_c17_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("qMVn/jiI/",), name='c17m7___format__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c17m7] Failed to create thread for __format__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c17m7___format__(target_func=target_func):
            print("Starting async task: async_call_c17m7___format__", file=stderr)
            time.sleep(0.000453) # Small delay
            try:
                target_func("p\xDE\xF4\xC5F")
            except Exception as e_async_call:
                print(f"[c17m7] Exception in async task async_call_c17m7___format__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c17m7___format__", file=stderr)
        fuzzer_async_tasks.append(async_call_c17m7___format__)

    try:
        res_c17m8 = callMethod("c17m8", instance_c17_popen, "close",
        verbose=True)
    except Exception as _argexc_c17m8:
        print("[c17m8] call skipped (argument build failed):", repr(_argexc_c17m8), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c17_popen, 'close')
    except Exception as e_get_target_func:
        print(f"[c17m8] Failed to get attribute close from instance_c17_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c17m8_close')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c17m8] Failed to create thread for close: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c17m8_close(target_func=target_func):
            print("Starting async task: async_call_c17m8_close", file=stderr)
            time.sleep(0.000290) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c17m8] Exception in async task async_call_c17m8_close: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c17m8_close", file=stderr)
        fuzzer_async_tasks.append(async_call_c17m8_close)

    try:
        res_c17m9 = callMethod("c17m9", instance_c17_popen, "kill",
        verbose=True)
    except Exception as _argexc_c17m9:
        print("[c17m9] call skipped (argument build failed):", repr(_argexc_c17m9), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c17_popen, 'kill')
    except Exception as e_get_target_func:
        print(f"[c17m9] Failed to get attribute kill from instance_c17_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c17m9_kill')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c17m9] Failed to create thread for kill: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c17m9_kill(target_func=target_func):
            print("Starting async task: async_call_c17m9_kill", file=stderr)
            time.sleep(0.000097) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c17m9] Exception in async task async_call_c17m9_kill: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c17m9_kill", file=stderr)
        fuzzer_async_tasks.append(async_call_c17m9_kill)

    try:
        res_c17m10 = callMethod("c17m10", instance_c17_popen, "__hash__",
        verbose=True)
    except Exception as _argexc_c17m10:
        print("[c17m10] call skipped (argument build failed):", repr(_argexc_c17m10), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c17_popen, '__hash__')
    except Exception as e_get_target_func:
        print(f"[c17m10] Failed to get attribute __hash__ from instance_c17_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c17m10___hash__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c17m10] Failed to create thread for __hash__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c17m10___hash__(target_func=target_func):
            print("Starting async task: async_call_c17m10___hash__", file=stderr)
            time.sleep(0.000080) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c17m10] Exception in async task async_call_c17m10___hash__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c17m10___hash__", file=stderr)
        fuzzer_async_tasks.append(async_call_c17m10___hash__)

    try:
        res_c17m11 = callMethod("c17m11", instance_c17_popen, "__repr__",
        verbose=True)
    except Exception as _argexc_c17m11:
        print("[c17m11] call skipped (argument build failed):", repr(_argexc_c17m11), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c17_popen, '__repr__')
    except Exception as e_get_target_func:
        print(f"[c17m11] Failed to get attribute __repr__ from instance_c17_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c17m11___repr__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c17m11] Failed to create thread for __repr__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c17m11___repr__(target_func=target_func):
            print("Starting async task: async_call_c17m11___repr__", file=stderr)
            time.sleep(0.000302) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c17m11] Exception in async task async_call_c17m11___repr__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c17m11___repr__", file=stderr)
        fuzzer_async_tasks.append(async_call_c17m11___repr__)

    try:
        res_c17m12 = callMethod("c17m12", instance_c17_popen, "__ge__",
            {True: -5528975,
             18: "\x00"},
        verbose=True)
    except Exception as _argexc_c17m12:
        print("[c17m12] call skipped (argument build failed):", repr(_argexc_c17m12), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c17_popen, '__ge__')
    except Exception as e_get_target_func:
        print(f"[c17m12] Failed to get attribute __ge__ from instance_c17_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(tricky_module,), name='c17m12___ge__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c17m12] Failed to create thread for __ge__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c17m12___ge__(target_func=target_func):
            print("Starting async task: async_call_c17m12___ge__", file=stderr)
            time.sleep(0.000355) # Small delay
            try:
                target_func("\x00")
            except Exception as e_async_call:
                print(f"[c17m12] Exception in async task async_call_c17m12___ge__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c17m12___ge__", file=stderr)
        fuzzer_async_tasks.append(async_call_c17m12___ge__)

    try:
        res_c17m13 = callMethod("c17m13", instance_c17_popen, "__init_subclass__",
            ReentrantClearList(),
        verbose=True)
    except Exception as _argexc_c17m13:
        print("[c17m13] call skipped (argument build failed):", repr(_argexc_c17m13), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c17_popen, '__init_subclass__')
    except Exception as e_get_target_func:
        print(f"[c17m13] Failed to get attribute __init_subclass__ from instance_c17_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=('/tmp/fusil-fixtures/fusil_fixture.bin',), name='c17m13___init_subclass__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c17m13] Failed to create thread for __init_subclass__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c17m13___init_subclass__(target_func=target_func):
            print("Starting async task: async_call_c17m13___init_subclass__", file=stderr)
            time.sleep(0.000457) # Small delay
            try:
                target_func(weird_instances['weird_float_2**63-1'])
            except Exception as e_async_call:
                print(f"[c17m13] Exception in async task async_call_c17m13___init_subclass__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c17m13___init_subclass__", file=stderr)
        fuzzer_async_tasks.append(async_call_c17m13___init_subclass__)

    try:
        res_c17m14 = callMethod("c17m14", instance_c17_popen, "__eq__",
            '/tmp/fusil-fixtures/fusil_fixture.bin',
        verbose=True)
    except Exception as _argexc_c17m14:
        print("[c17m14] call skipped (argument build failed):", repr(_argexc_c17m14), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c17_popen, '__eq__')
    except Exception as e_get_target_func:
        print(f"[c17m14] Failed to get attribute __eq__ from instance_c17_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(HashBomb(),), name='c17m14___eq__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c17m14] Failed to create thread for __eq__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c17m14___eq__(target_func=target_func):
            print("Starting async task: async_call_c17m14___eq__", file=stderr)
            time.sleep(0.000589) # Small delay
            try:
                target_func(list[weird_classes['weird_deque']] | weird_classes['weird_Queue'] | big_union)
            except Exception as e_async_call:
                print(f"[c17m14] Exception in async task async_call_c17m14___eq__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c17m14___eq__", file=stderr)
        fuzzer_async_tasks.append(async_call_c17m14___eq__)

    try:
        res_c17m15 = callMethod("c17m15", instance_c17_popen, "__new__",
            weird_classes['weird_Queue'],
            int,
            weird_instances['weird_str_types'],
        verbose=True)
    except Exception as _argexc_c17m15:
        print("[c17m15] call skipped (argument build failed):", repr(_argexc_c17m15), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c17_popen, '__new__')
    except Exception as e_get_target_func:
        print(f"[c17m15] Failed to get attribute __new__ from instance_c17_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(bytearray(b"test"), LyingInplace(), -589.1475), name='c17m15___new__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c17m15] Failed to create thread for __new__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c17m15___new__(target_func=target_func):
            print("Starting async task: async_call_c17m15___new__", file=stderr)
            time.sleep(0.000332) # Small delay
            try:
                target_func(TypeFlipIterator(), None, "/YTZBVFFufA08-")
            except Exception as e_async_call:
                print(f"[c17m15] Exception in async task async_call_c17m15___new__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c17m15___new__", file=stderr)
        fuzzer_async_tasks.append(async_call_c17m15___new__)

    print(f"--- Finished fuzzing instance: instance_c17_popen ---", file=stderr)

    del instance_c17_popen # Cleanup instance
    print("[c17] -explicit garbage collection for class instance-", file=stderr)
    collect()

print("[c18] Attempting to instantiate class: Popen", file=stderr)
instance_c18_popen = None # Initialize instance variable
try:
    instance_c18_popen = callFunc('c18_init', 'Popen',
        ShiftyEq(),
      )
except Exception as e_instantiate:
    instance_c18_popen = None
    print("[c18] Failed to instantiate Popen: {e_instantiate.__class__.__name__} {e_instantiate}", file=stderr)
    instance_c18_popen = None

try:
    print(f"--- (Depth 0) Dispatching Fuzz for: {instance_c18_popen!r} (hint: Popen, prefix: c18_popen_ops) ---", file=stderr)
except Exception as e:
    print(f"--- (Depth 0) Error calling repr() prefix: c18_popen_ops) ---", file=stderr)
if instance_c18_popen is not None:
    if skip_trivial_type(instance_c18_popen):
        print(f'Skipping deep diving on instance_c18_popen {type(instance_c18_popen)}', file=stderr)
    try:
        print(f'Instance {instance_c18_popen!r} (actual type {type(instance_c18_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    except Exception as e:
        print(f'Error printing instance repr() { e } (actual type {type(instance_c18_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    if skip_trivial_type(instance_c18_popen):
        print(f'Skipping deep diving on instance_c18_popen {type(instance_c18_popen)}', file=stderr)
    else:
        print(f'Instance instance_c18_popen (type {type(instance_c18_popen).__name__}) has no specific fuzzer, doing generic calls.', file=stderr)
        c18_popen_ops_generic_methods = []
        try:
            for c18_popen_ops_generic_attr_name in dir(instance_c18_popen):
                if c18_popen_ops_generic_attr_name.startswith('_'): continue
                try:
                    c18_popen_ops_generic_attr_val = getattr(instance_c18_popen, c18_popen_ops_generic_attr_name)
                    if callable(c18_popen_ops_generic_attr_val) and c18_popen_ops_generic_attr_name not in _FUSIL_METHOD_BLACKLIST: c18_popen_ops_generic_methods.append((c18_popen_ops_generic_attr_name, c18_popen_ops_generic_attr_val))
                except Exception: pass
        except Exception: c18_popen_ops_generic_methods = [] # Failed to get methods
        if c18_popen_ops_generic_methods:
            print(f'Found {len(c18_popen_ops_generic_methods)} callable methods for generic fuzzing of instance_c18_popen', file=stderr)
            for _i_c18_popen_ops_generic in range(min(len(c18_popen_ops_generic_methods), 15)):
                c18_popen_ops_generic_method_name_to_call, c18_popen_ops_generic_method_obj_to_call = choice(c18_popen_ops_generic_methods)
                # Conceptual call to generic method fuzzer
                if c18_popen_ops_generic_method_name_to_call not in _FUSIL_METHOD_BLACKLIST: callMethod(f'c18_popen_ops_generic_gen{_i_c18_popen_ops_generic}', instance_c18_popen, c18_popen_ops_generic_method_name_to_call)

if instance_c18_popen is not None and instance_c18_popen is not SENTINEL_VALUE:
    print(f"--- Fuzzing instance: instance_c18_popen (type hint: Popen, prefix: c18m) ---", file=stderr)
    if skip_trivial_type(instance_c18_popen):
        print(f'Skipping deep diving on instance_c18_popen {type(instance_c18_popen)}', file=stderr)
    # General method fuzzing for instance_c18_popen
    try:
        res_c18m1 = callMethod("c18m1", instance_c18_popen, "__init__",
            tricky_instance,
        verbose=True)
    except Exception as _argexc_c18m1:
        print("[c18m1] call skipped (argument build failed):", repr(_argexc_c18m1), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c18_popen, '__init__')
    except Exception as e_get_target_func:
        print(f"[c18m1] Failed to get attribute __init__ from instance_c18_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(tricky_code,), name='c18m1___init__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c18m1] Failed to create thread for __init__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c18m1___init__(target_func=target_func):
            print("Starting async task: async_call_c18m1___init__", file=stderr)
            time.sleep(0.000887) # Small delay
            try:
                target_func(Exception('fuzzer_generated_exception'))
            except Exception as e_async_call:
                print(f"[c18m1] Exception in async task async_call_c18m1___init__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c18m1___init__", file=stderr)
        fuzzer_async_tasks.append(async_call_c18m1___init__)

    try:
        res_c18m2 = callMethod("c18m2", instance_c18_popen, "__reduce__",
        verbose=True)
    except Exception as _argexc_c18m2:
        print("[c18m2] call skipped (argument build failed):", repr(_argexc_c18m2), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c18_popen, '__reduce__')
    except Exception as e_get_target_func:
        print(f"[c18m2] Failed to get attribute __reduce__ from instance_c18_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c18m2___reduce__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c18m2] Failed to create thread for __reduce__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c18m2___reduce__(target_func=target_func):
            print("Starting async task: async_call_c18m2___reduce__", file=stderr)
            time.sleep(0.000850) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c18m2] Exception in async task async_call_c18m2___reduce__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c18m2___reduce__", file=stderr)
        fuzzer_async_tasks.append(async_call_c18m2___reduce__)

    try:
        res_c18m3 = callMethod("c18m3", instance_c18_popen, "__init__",
            11,
        verbose=True)
    except Exception as _argexc_c18m3:
        print("[c18m3] call skipped (argument build failed):", repr(_argexc_c18m3), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c18_popen, '__init__')
    except Exception as e_get_target_func:
        print(f"[c18m3] Failed to get attribute __init__ from instance_c18_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(ShiftyEq(),), name='c18m3___init__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c18m3] Failed to create thread for __init__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c18m3___init__(target_func=target_func):
            print("Starting async task: async_call_c18m3___init__", file=stderr)
            time.sleep(0.000783) # Small delay
            try:
                target_func(errback)
            except Exception as e_async_call:
                print(f"[c18m3] Exception in async task async_call_c18m3___init__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c18m3___init__", file=stderr)
        fuzzer_async_tasks.append(async_call_c18m3___init__)

    try:
        res_c18m4 = callMethod("c18m4", instance_c18_popen, "__reduce__",
        verbose=True)
    except Exception as _argexc_c18m4:
        print("[c18m4] call skipped (argument build failed):", repr(_argexc_c18m4), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c18_popen, '__reduce__')
    except Exception as e_get_target_func:
        print(f"[c18m4] Failed to get attribute __reduce__ from instance_c18_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c18m4___reduce__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c18m4] Failed to create thread for __reduce__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c18m4___reduce__(target_func=target_func):
            print("Starting async task: async_call_c18m4___reduce__", file=stderr)
            time.sleep(0.000875) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c18m4] Exception in async task async_call_c18m4___reduce__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c18m4___reduce__", file=stderr)
        fuzzer_async_tasks.append(async_call_c18m4___reduce__)

    try:
        res_c18m5 = callMethod("c18m5", instance_c18_popen, "__reduce__",
        verbose=True)
    except Exception as _argexc_c18m5:
        print("[c18m5] call skipped (argument build failed):", repr(_argexc_c18m5), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c18_popen, '__reduce__')
    except Exception as e_get_target_func:
        print(f"[c18m5] Failed to get attribute __reduce__ from instance_c18_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c18m5___reduce__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c18m5] Failed to create thread for __reduce__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c18m5___reduce__(target_func=target_func):
            print("Starting async task: async_call_c18m5___reduce__", file=stderr)
            time.sleep(0.000231) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c18m5] Exception in async task async_call_c18m5___reduce__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c18m5___reduce__", file=stderr)
        fuzzer_async_tasks.append(async_call_c18m5___reduce__)

    try:
        res_c18m6 = callMethod("c18m6", instance_c18_popen, "_send_signal",
            "\u5A33\u1032\uF63F\u8981\u86E2",
        verbose=True)
    except Exception as _argexc_c18m6:
        print("[c18m6] call skipped (argument build failed):", repr(_argexc_c18m6), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c18_popen, '_send_signal')
    except Exception as e_get_target_func:
        print(f"[c18m6] Failed to get attribute _send_signal from instance_c18_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(weird_instances['weird_float_neg_sys_maxsize'],), name='c18m6__send_signal')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c18m6] Failed to create thread for _send_signal: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c18m6__send_signal(target_func=target_func):
            print("Starting async task: async_call_c18m6__send_signal", file=stderr)
            time.sleep(0.000341) # Small delay
            try:
                target_func(-7.98)
            except Exception as e_async_call:
                print(f"[c18m6] Exception in async task async_call_c18m6__send_signal: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c18m6__send_signal", file=stderr)
        fuzzer_async_tasks.append(async_call_c18m6__send_signal)

    try:
        res_c18m7 = callMethod("c18m7", instance_c18_popen, "__setattr__",
            6,
            GrowingLen(),
        verbose=True)
    except Exception as _argexc_c18m7:
        print("[c18m7] call skipped (argument build failed):", repr(_argexc_c18m7), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c18_popen, '__setattr__')
    except Exception as e_get_target_func:
        print(f"[c18m7] Failed to get attribute __setattr__ from instance_c18_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(None, "JO9NKc-5TD//y5OwhJ/is4XTQ4rRSS49iMG/../WCGiqvq/."), name='c18m7___setattr__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c18m7] Failed to create thread for __setattr__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c18m7___setattr__(target_func=target_func):
            print("Starting async task: async_call_c18m7___setattr__", file=stderr)
            time.sleep(0.000706) # Small delay
            try:
                target_func("3aoGX1fzAbuzn_gq6lu2W/nQbtfx1Qrm2_Owguhtj5S49RvueeVD7CkRTqWikh8mWFQECAdkwkq1xgo/Q4m4fR7IncJhK", tricky_deep_genericalias)
            except Exception as e_async_call:
                print(f"[c18m7] Exception in async task async_call_c18m7___setattr__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c18m7___setattr__", file=stderr)
        fuzzer_async_tasks.append(async_call_c18m7___setattr__)

    try:
        res_c18m8 = callMethod("c18m8", instance_c18_popen, "_send_signal",
            EqBomb(),
        verbose=True)
    except Exception as _argexc_c18m8:
        print("[c18m8] call skipped (argument build failed):", repr(_argexc_c18m8), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c18_popen, '_send_signal')
    except Exception as e_get_target_func:
        print(f"[c18m8] Failed to get attribute _send_signal from instance_c18_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(4,), name='c18m8__send_signal')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c18m8] Failed to create thread for _send_signal: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c18m8__send_signal(target_func=target_func):
            print("Starting async task: async_call_c18m8__send_signal", file=stderr)
            time.sleep(0.000116) # Small delay
            try:
                target_func(weird_classes['weird_str'])
            except Exception as e_async_call:
                print(f"[c18m8] Exception in async task async_call_c18m8__send_signal: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c18m8__send_signal", file=stderr)
        fuzzer_async_tasks.append(async_call_c18m8__send_signal)

    try:
        res_c18m9 = callMethod("c18m9", instance_c18_popen, "__ne__",
            GrowingLen(),
        verbose=True)
    except Exception as _argexc_c18m9:
        print("[c18m9] call skipped (argument build failed):", repr(_argexc_c18m9), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c18_popen, '__ne__')
    except Exception as e_get_target_func:
        print(f"[c18m9] Failed to get attribute __ne__ from instance_c18_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(r"di\sdclu?R.BJk.f.A\wiC\bQdcF..s.\S.\d\S.\bDObC",), name='c18m9___ne__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c18m9] Failed to create thread for __ne__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c18m9___ne__(target_func=target_func):
            print("Starting async task: async_call_c18m9___ne__", file=stderr)
            time.sleep(0.000621) # Small delay
            try:
                target_func(True)
            except Exception as e_async_call:
                print(f"[c18m9] Exception in async task async_call_c18m9___ne__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c18m9___ne__", file=stderr)
        fuzzer_async_tasks.append(async_call_c18m9___ne__)

    try:
        res_c18m10 = callMethod("c18m10", instance_c18_popen, "__ge__",
            weird_classes['weird_OrderedDict'],
        verbose=True)
    except Exception as _argexc_c18m10:
        print("[c18m10] call skipped (argument build failed):", repr(_argexc_c18m10), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c18_popen, '__ge__')
    except Exception as e_get_target_func:
        print(f"[c18m10] Failed to get attribute __ge__ from instance_c18_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(False,), name='c18m10___ge__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c18m10] Failed to create thread for __ge__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c18m10___ge__(target_func=target_func):
            print("Starting async task: async_call_c18m10___ge__", file=stderr)
            time.sleep(0.000257) # Small delay
            try:
                target_func(HashBomb())
            except Exception as e_async_call:
                print(f"[c18m10] Exception in async task async_call_c18m10___ge__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c18m10___ge__", file=stderr)
        fuzzer_async_tasks.append(async_call_c18m10___ge__)

    try:
        res_c18m11 = callMethod("c18m11", instance_c18_popen, "poll",
            bytearray(b"test"),
        verbose=True)
    except Exception as _argexc_c18m11:
        print("[c18m11] call skipped (argument build failed):", repr(_argexc_c18m11), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c18_popen, 'poll')
    except Exception as e_get_target_func:
        print(f"[c18m11] Failed to get attribute poll from instance_c18_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(errback,), name='c18m11_poll')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c18m11] Failed to create thread for poll: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c18m11_poll(target_func=target_func):
            print("Starting async task: async_call_c18m11_poll", file=stderr)
            time.sleep(0.000804) # Small delay
            try:
                target_func(b"\x1C\x93\xA6\xCB\xC6\xBD\x0A\x80\x30\x82\xFD\x49\xD5\x8B\x33\x63")
            except Exception as e_async_call:
                print(f"[c18m11] Exception in async task async_call_c18m11_poll: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c18m11_poll", file=stderr)
        fuzzer_async_tasks.append(async_call_c18m11_poll)

    try:
        res_c18m12 = callMethod("c18m12", instance_c18_popen, "__subclasshook__",
            None,
        verbose=True)
    except Exception as _argexc_c18m12:
        print("[c18m12] call skipped (argument build failed):", repr(_argexc_c18m12), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c18_popen, '__subclasshook__')
    except Exception as e_get_target_func:
        print(f"[c18m12] Failed to get attribute __subclasshook__ from instance_c18_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("\xD5\x01",), name='c18m12___subclasshook__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c18m12] Failed to create thread for __subclasshook__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c18m12___subclasshook__(target_func=target_func):
            print("Starting async task: async_call_c18m12___subclasshook__", file=stderr)
            time.sleep(0.000368) # Small delay
            try:
                target_func(dict[weird_classes['weird_bytearray']])
            except Exception as e_async_call:
                print(f"[c18m12] Exception in async task async_call_c18m12___subclasshook__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c18m12___subclasshook__", file=stderr)
        fuzzer_async_tasks.append(async_call_c18m12___subclasshook__)

    try:
        res_c18m13 = callMethod("c18m13", instance_c18_popen, "terminate",
        verbose=True)
    except Exception as _argexc_c18m13:
        print("[c18m13] call skipped (argument build failed):", repr(_argexc_c18m13), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c18_popen, 'terminate')
    except Exception as e_get_target_func:
        print(f"[c18m13] Failed to get attribute terminate from instance_c18_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c18m13_terminate')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c18m13] Failed to create thread for terminate: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c18m13_terminate(target_func=target_func):
            print("Starting async task: async_call_c18m13_terminate", file=stderr)
            time.sleep(0.000018) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c18m13] Exception in async task async_call_c18m13_terminate: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c18m13_terminate", file=stderr)
        fuzzer_async_tasks.append(async_call_c18m13_terminate)

    try:
        res_c18m14 = callMethod("c18m14", instance_c18_popen, "__getstate__",
        verbose=True)
    except Exception as _argexc_c18m14:
        print("[c18m14] call skipped (argument build failed):", repr(_argexc_c18m14), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c18_popen, '__getstate__')
    except Exception as e_get_target_func:
        print(f"[c18m14] Failed to get attribute __getstate__ from instance_c18_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c18m14___getstate__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c18m14] Failed to create thread for __getstate__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c18m14___getstate__(target_func=target_func):
            print("Starting async task: async_call_c18m14___getstate__", file=stderr)
            time.sleep(0.000158) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c18m14] Exception in async task async_call_c18m14___getstate__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c18m14___getstate__", file=stderr)
        fuzzer_async_tasks.append(async_call_c18m14___getstate__)

    try:
        res_c18m15 = callMethod("c18m15", instance_c18_popen, "__reduce__",
        verbose=True)
    except Exception as _argexc_c18m15:
        print("[c18m15] call skipped (argument build failed):", repr(_argexc_c18m15), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c18_popen, '__reduce__')
    except Exception as e_get_target_func:
        print(f"[c18m15] Failed to get attribute __reduce__ from instance_c18_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c18m15___reduce__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c18m15] Failed to create thread for __reduce__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c18m15___reduce__(target_func=target_func):
            print("Starting async task: async_call_c18m15___reduce__", file=stderr)
            time.sleep(0.000054) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c18m15] Exception in async task async_call_c18m15___reduce__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c18m15___reduce__", file=stderr)
        fuzzer_async_tasks.append(async_call_c18m15___reduce__)

    print(f"--- Finished fuzzing instance: instance_c18_popen ---", file=stderr)

    del instance_c18_popen # Cleanup instance
    print("[c18] -explicit garbage collection for class instance-", file=stderr)
    collect()

print("[c19] Attempting to instantiate class: Popen", file=stderr)
instance_c19_popen = None # Initialize instance variable
try:
    instance_c19_popen = callFunc('c19_init', 'Popen',
        LyingInplace(),
      )
except Exception as e_instantiate:
    instance_c19_popen = None
    print("[c19] Failed to instantiate Popen: {e_instantiate.__class__.__name__} {e_instantiate}", file=stderr)
    instance_c19_popen = None

try:
    print(f"--- (Depth 0) Dispatching Fuzz for: {instance_c19_popen!r} (hint: Popen, prefix: c19_popen_ops) ---", file=stderr)
except Exception as e:
    print(f"--- (Depth 0) Error calling repr() prefix: c19_popen_ops) ---", file=stderr)
if instance_c19_popen is not None:
    if skip_trivial_type(instance_c19_popen):
        print(f'Skipping deep diving on instance_c19_popen {type(instance_c19_popen)}', file=stderr)
    try:
        print(f'Instance {instance_c19_popen!r} (actual type {type(instance_c19_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    except Exception as e:
        print(f'Error printing instance repr() { e } (actual type {type(instance_c19_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    if skip_trivial_type(instance_c19_popen):
        print(f'Skipping deep diving on instance_c19_popen {type(instance_c19_popen)}', file=stderr)
    else:
        print(f'Instance instance_c19_popen (type {type(instance_c19_popen).__name__}) has no specific fuzzer, doing generic calls.', file=stderr)
        c19_popen_ops_generic_methods = []
        try:
            for c19_popen_ops_generic_attr_name in dir(instance_c19_popen):
                if c19_popen_ops_generic_attr_name.startswith('_'): continue
                try:
                    c19_popen_ops_generic_attr_val = getattr(instance_c19_popen, c19_popen_ops_generic_attr_name)
                    if callable(c19_popen_ops_generic_attr_val) and c19_popen_ops_generic_attr_name not in _FUSIL_METHOD_BLACKLIST: c19_popen_ops_generic_methods.append((c19_popen_ops_generic_attr_name, c19_popen_ops_generic_attr_val))
                except Exception: pass
        except Exception: c19_popen_ops_generic_methods = [] # Failed to get methods
        if c19_popen_ops_generic_methods:
            print(f'Found {len(c19_popen_ops_generic_methods)} callable methods for generic fuzzing of instance_c19_popen', file=stderr)
            for _i_c19_popen_ops_generic in range(min(len(c19_popen_ops_generic_methods), 15)):
                c19_popen_ops_generic_method_name_to_call, c19_popen_ops_generic_method_obj_to_call = choice(c19_popen_ops_generic_methods)
                # Conceptual call to generic method fuzzer
                if c19_popen_ops_generic_method_name_to_call not in _FUSIL_METHOD_BLACKLIST: callMethod(f'c19_popen_ops_generic_gen{_i_c19_popen_ops_generic}', instance_c19_popen, c19_popen_ops_generic_method_name_to_call)

if instance_c19_popen is not None and instance_c19_popen is not SENTINEL_VALUE:
    print(f"--- Fuzzing instance: instance_c19_popen (type hint: Popen, prefix: c19m) ---", file=stderr)
    if skip_trivial_type(instance_c19_popen):
        print(f'Skipping deep diving on instance_c19_popen {type(instance_c19_popen)}', file=stderr)
    # General method fuzzing for instance_c19_popen
    try:
        res_c19m1 = callMethod("c19m1", instance_c19_popen, "__setattr__",
            tuple[weird_classes['weird_tuple']],
            GrowingLen(),
        verbose=True)
    except Exception as _argexc_c19m1:
        print("[c19m1] call skipped (argument build failed):", repr(_argexc_c19m1), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c19_popen, '__setattr__')
    except Exception as e_get_target_func:
        print(f"[c19m1] Failed to get attribute __setattr__ from instance_c19_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(MagicMock, MutatingIterable()), name='c19m1___setattr__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c19m1] Failed to create thread for __setattr__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c19m1___setattr__(target_func=target_func):
            print("Starting async task: async_call_c19m1___setattr__", file=stderr)
            time.sleep(0.000166) # Small delay
            try:
                target_func("\x00", tricky_simplenamespace)
            except Exception as e_async_call:
                print(f"[c19m1] Exception in async task async_call_c19m1___setattr__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c19m1___setattr__", file=stderr)
        fuzzer_async_tasks.append(async_call_c19m1___setattr__)

    try:
        res_c19m2 = callMethod("c19m2", instance_c19_popen, "__le__",
            weird_instances['weird_set_printable'],
        verbose=True)
    except Exception as _argexc_c19m2:
        print("[c19m2] call skipped (argument build failed):", repr(_argexc_c19m2), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c19_popen, '__le__')
    except Exception as e_get_target_func:
        print(f"[c19m2] Failed to get attribute __le__ from instance_c19_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(None,), name='c19m2___le__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c19m2] Failed to create thread for __le__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c19m2___le__(target_func=target_func):
            print("Starting async task: async_call_c19m2___le__", file=stderr)
            time.sleep(0.000754) # Small delay
            try:
                target_func("\uE9C4\u82B6\u3238\uC8D6\u660A\uED2D\u6D2C\u0572\u3F18\u4F47\uA803\u2C97\u90FD\u6A9B")
            except Exception as e_async_call:
                print(f"[c19m2] Exception in async task async_call_c19m2___le__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c19m2___le__", file=stderr)
        fuzzer_async_tasks.append(async_call_c19m2___le__)

    try:
        res_c19m3 = callMethod("c19m3", instance_c19_popen, "__setattr__",
            "\xD7\x8B\x17\x94\xDFOB\xEC\x03T6a\xB8\xECu\xE4\xB7\xE7c{",
            tricky_instance,
        verbose=True)
    except Exception as _argexc_c19m3:
        print("[c19m3] call skipped (argument build failed):", repr(_argexc_c19m3), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c19_popen, '__setattr__')
    except Exception as e_get_target_func:
        print(f"[c19m3] Failed to get attribute __setattr__ from instance_c19_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(-8811204142326589617, weird_classes['weird_complex']), name='c19m3___setattr__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c19m3] Failed to create thread for __setattr__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c19m3___setattr__(target_func=target_func):
            print("Starting async task: async_call_c19m3___setattr__", file=stderr)
            time.sleep(0.000064) # Small delay
            try:
                target_func(StatefulHashType, -17)
            except Exception as e_async_call:
                print(f"[c19m3] Exception in async task async_call_c19m3___setattr__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c19m3___setattr__", file=stderr)
        fuzzer_async_tasks.append(async_call_c19m3___setattr__)

    try:
        res_c19m4 = callMethod("c19m4", instance_c19_popen, "__subclasshook__",
            errback,
        verbose=True)
    except Exception as _argexc_c19m4:
        print("[c19m4] call skipped (argument build failed):", repr(_argexc_c19m4), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c19_popen, '__subclasshook__')
    except Exception as e_get_target_func:
        print(f"[c19m4] Failed to get attribute __subclasshook__ from instance_c19_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(-34.64,), name='c19m4___subclasshook__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c19m4] Failed to create thread for __subclasshook__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c19m4___subclasshook__(target_func=target_func):
            print("Starting async task: async_call_c19m4___subclasshook__", file=stderr)
            time.sleep(0.000595) # Small delay
            try:
                target_func(LyingInstanceCheckType)
            except Exception as e_async_call:
                print(f"[c19m4] Exception in async task async_call_c19m4___subclasshook__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c19m4___subclasshook__", file=stderr)
        fuzzer_async_tasks.append(async_call_c19m4___subclasshook__)

    try:
        res_c19m5 = callMethod("c19m5", instance_c19_popen, "__init__",
            -70.3982,
            '/tmp/fusil-fixtures/fusil_fixture.txt',
        verbose=True)
    except Exception as _argexc_c19m5:
        print("[c19m5] call skipped (argument build failed):", repr(_argexc_c19m5), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c19_popen, '__init__')
    except Exception as e_get_target_func:
        print(f"[c19m5] Failed to get attribute __init__ from instance_c19_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(LenBomb(), Exception('fuzzer_generated_exception')), name='c19m5___init__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c19m5] Failed to create thread for __init__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c19m5___init__(target_func=target_func):
            print("Starting async task: async_call_c19m5___init__", file=stderr)
            time.sleep(0.000957) # Small delay
            try:
                target_func(False, weird_instances['weird_OrderedDict_tricky_strs'])
            except Exception as e_async_call:
                print(f"[c19m5] Exception in async task async_call_c19m5___init__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c19m5___init__", file=stderr)
        fuzzer_async_tasks.append(async_call_c19m5___init__)

    try:
        res_c19m6 = callMethod("c19m6", instance_c19_popen, "terminate",
        verbose=True)
    except Exception as _argexc_c19m6:
        print("[c19m6] call skipped (argument build failed):", repr(_argexc_c19m6), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c19_popen, 'terminate')
    except Exception as e_get_target_func:
        print(f"[c19m6] Failed to get attribute terminate from instance_c19_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c19m6_terminate')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c19m6] Failed to create thread for terminate: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c19m6_terminate(target_func=target_func):
            print("Starting async task: async_call_c19m6_terminate", file=stderr)
            time.sleep(0.000184) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c19m6] Exception in async task async_call_c19m6_terminate: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c19m6_terminate", file=stderr)
        fuzzer_async_tasks.append(async_call_c19m6_terminate)

    try:
        res_c19m7 = callMethod("c19m7", instance_c19_popen, "__subclasshook__",
            -746957137926,
        verbose=True)
    except Exception as _argexc_c19m7:
        print("[c19m7] call skipped (argument build failed):", repr(_argexc_c19m7), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c19_popen, '__subclasshook__')
    except Exception as e_get_target_func:
        print(f"[c19m7] Failed to get attribute __subclasshook__ from instance_c19_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(weird_instances['weird_Decimal_sys_maxsize_minus_one'],), name='c19m7___subclasshook__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c19m7] Failed to create thread for __subclasshook__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c19m7___subclasshook__(target_func=target_func):
            print("Starting async task: async_call_c19m7___subclasshook__", file=stderr)
            time.sleep(0.000999) # Small delay
            try:
                target_func(None)
            except Exception as e_async_call:
                print(f"[c19m7] Exception in async task async_call_c19m7___subclasshook__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c19m7___subclasshook__", file=stderr)
        fuzzer_async_tasks.append(async_call_c19m7___subclasshook__)

    try:
        res_c19m8 = callMethod("c19m8", instance_c19_popen, "__subclasshook__",
            RaisingInstanceCheckType,
            errback,
        verbose=True)
    except Exception as _argexc_c19m8:
        print("[c19m8] call skipped (argument build failed):", repr(_argexc_c19m8), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c19_popen, '__subclasshook__')
    except Exception as e_get_target_func:
        print(f"[c19m8] Failed to get attribute __subclasshook__ from instance_c19_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(-36521, weird_classes['weird_float']), name='c19m8___subclasshook__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c19m8] Failed to create thread for __subclasshook__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c19m8___subclasshook__(target_func=target_func):
            print("Starting async task: async_call_c19m8___subclasshook__", file=stderr)
            time.sleep(0.000767) # Small delay
            try:
                target_func(False, weird_instances['weird_Decimal_-2**31'])
            except Exception as e_async_call:
                print(f"[c19m8] Exception in async task async_call_c19m8___subclasshook__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c19m8___subclasshook__", file=stderr)
        fuzzer_async_tasks.append(async_call_c19m8___subclasshook__)

    try:
        res_c19m9 = callMethod("c19m9", instance_c19_popen, "__reduce_ex__",
            "J7l/ETMOe57z/oVc0c/./z-",
        verbose=True)
    except Exception as _argexc_c19m9:
        print("[c19m9] call skipped (argument build failed):", repr(_argexc_c19m9), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c19_popen, '__reduce_ex__')
    except Exception as e_get_target_func:
        print(f"[c19m9] Failed to get attribute __reduce_ex__ from instance_c19_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(MutatingIterable(),), name='c19m9___reduce_ex__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c19m9] Failed to create thread for __reduce_ex__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c19m9___reduce_ex__(target_func=target_func):
            print("Starting async task: async_call_c19m9___reduce_ex__", file=stderr)
            time.sleep(0.000909) # Small delay
            try:
                target_func(False)
            except Exception as e_async_call:
                print(f"[c19m9] Exception in async task async_call_c19m9___reduce_ex__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c19m9___reduce_ex__", file=stderr)
        fuzzer_async_tasks.append(async_call_c19m9___reduce_ex__)

    try:
        res_c19m10 = callMethod("c19m10", instance_c19_popen, "__reduce__",
        verbose=True)
    except Exception as _argexc_c19m10:
        print("[c19m10] call skipped (argument build failed):", repr(_argexc_c19m10), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c19_popen, '__reduce__')
    except Exception as e_get_target_func:
        print(f"[c19m10] Failed to get attribute __reduce__ from instance_c19_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c19m10___reduce__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c19m10] Failed to create thread for __reduce__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c19m10___reduce__(target_func=target_func):
            print("Starting async task: async_call_c19m10___reduce__", file=stderr)
            time.sleep(0.000138) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c19m10] Exception in async task async_call_c19m10___reduce__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c19m10___reduce__", file=stderr)
        fuzzer_async_tasks.append(async_call_c19m10___reduce__)

    try:
        res_c19m11 = callMethod("c19m11", instance_c19_popen, "__dir__",
        verbose=True)
    except Exception as _argexc_c19m11:
        print("[c19m11] call skipped (argument build failed):", repr(_argexc_c19m11), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c19_popen, '__dir__')
    except Exception as e_get_target_func:
        print(f"[c19m11] Failed to get attribute __dir__ from instance_c19_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c19m11___dir__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c19m11] Failed to create thread for __dir__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c19m11___dir__(target_func=target_func):
            print("Starting async task: async_call_c19m11___dir__", file=stderr)
            time.sleep(0.000800) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c19m11] Exception in async task async_call_c19m11___dir__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c19m11___dir__", file=stderr)
        fuzzer_async_tasks.append(async_call_c19m11___dir__)

    try:
        res_c19m12 = callMethod("c19m12", instance_c19_popen, "__eq__",
            '/tmp/fusil-fixtures/fusil_fixture.bin',
            WrongTypeFile(),
        verbose=True)
    except Exception as _argexc_c19m12:
        print("[c19m12] call skipped (argument build failed):", repr(_argexc_c19m12), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c19_popen, '__eq__')
    except Exception as e_get_target_func:
        print(f"[c19m12] Failed to get attribute __eq__ from instance_c19_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(Exception('fuzzer_generated_exception'), -1j), name='c19m12___eq__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c19m12] Failed to create thread for __eq__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c19m12___eq__(target_func=target_func):
            print("Starting async task: async_call_c19m12___eq__", file=stderr)
            time.sleep(0.000902) # Small delay
            try:
                target_func(Exception('fuzzer_generated_exception'), weird_instances['weird_complex_-2**31'])
            except Exception as e_async_call:
                print(f"[c19m12] Exception in async task async_call_c19m12___eq__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c19m12___eq__", file=stderr)
        fuzzer_async_tasks.append(async_call_c19m12___eq__)

    try:
        res_c19m13 = callMethod("c19m13", instance_c19_popen, "__reduce_ex__",
            "CLrnIoQVXaGwr1QXxopoBSdfNMhwf3i2xs/VhhpsmuTT8ZxclI/N4ANA5/n/.//lSj8/6/z/t/9",
        verbose=True)
    except Exception as _argexc_c19m13:
        print("[c19m13] call skipped (argument build failed):", repr(_argexc_c19m13), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c19_popen, '__reduce_ex__')
    except Exception as e_get_target_func:
        print(f"[c19m13] Failed to get attribute __reduce_ex__ from instance_c19_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(FilenoBomb(),), name='c19m13___reduce_ex__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c19m13] Failed to create thread for __reduce_ex__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c19m13___reduce_ex__(target_func=target_func):
            print("Starting async task: async_call_c19m13___reduce_ex__", file=stderr)
            time.sleep(0.000225) # Small delay
            try:
                target_func(object())
            except Exception as e_async_call:
                print(f"[c19m13] Exception in async task async_call_c19m13___reduce_ex__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c19m13___reduce_ex__", file=stderr)
        fuzzer_async_tasks.append(async_call_c19m13___reduce_ex__)

    try:
        res_c19m14 = callMethod("c19m14", instance_c19_popen, "__reduce__",
        verbose=True)
    except Exception as _argexc_c19m14:
        print("[c19m14] call skipped (argument build failed):", repr(_argexc_c19m14), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c19_popen, '__reduce__')
    except Exception as e_get_target_func:
        print(f"[c19m14] Failed to get attribute __reduce__ from instance_c19_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c19m14___reduce__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c19m14] Failed to create thread for __reduce__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c19m14___reduce__(target_func=target_func):
            print("Starting async task: async_call_c19m14___reduce__", file=stderr)
            time.sleep(0.000266) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c19m14] Exception in async task async_call_c19m14___reduce__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c19m14___reduce__", file=stderr)
        fuzzer_async_tasks.append(async_call_c19m14___reduce__)

    try:
        res_c19m15 = callMethod("c19m15", instance_c19_popen, "__dir__",
        verbose=True)
    except Exception as _argexc_c19m15:
        print("[c19m15] call skipped (argument build failed):", repr(_argexc_c19m15), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c19_popen, '__dir__')
    except Exception as e_get_target_func:
        print(f"[c19m15] Failed to get attribute __dir__ from instance_c19_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c19m15___dir__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c19m15] Failed to create thread for __dir__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c19m15___dir__(target_func=target_func):
            print("Starting async task: async_call_c19m15___dir__", file=stderr)
            time.sleep(0.000741) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c19m15] Exception in async task async_call_c19m15___dir__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c19m15___dir__", file=stderr)
        fuzzer_async_tasks.append(async_call_c19m15___dir__)

    print(f"--- Finished fuzzing instance: instance_c19_popen ---", file=stderr)

    del instance_c19_popen # Cleanup instance
    print("[c19] -explicit garbage collection for class instance-", file=stderr)
    collect()

print("[c20] Attempting to instantiate class: Popen", file=stderr)
instance_c20_popen = None # Initialize instance variable
try:
    instance_c20_popen = callFunc('c20_init', 'Popen',
        "\uAD36\u2E99\u3500\u6145\u70F1\uD3FA\u834C\uFC5A",
      )
except Exception as e_instantiate:
    instance_c20_popen = None
    print("[c20] Failed to instantiate Popen: {e_instantiate.__class__.__name__} {e_instantiate}", file=stderr)
    instance_c20_popen = None

try:
    print(f"--- (Depth 0) Dispatching Fuzz for: {instance_c20_popen!r} (hint: Popen, prefix: c20_popen_ops) ---", file=stderr)
except Exception as e:
    print(f"--- (Depth 0) Error calling repr() prefix: c20_popen_ops) ---", file=stderr)
if instance_c20_popen is not None:
    if skip_trivial_type(instance_c20_popen):
        print(f'Skipping deep diving on instance_c20_popen {type(instance_c20_popen)}', file=stderr)
    try:
        print(f'Instance {instance_c20_popen!r} (actual type {type(instance_c20_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    except Exception as e:
        print(f'Error printing instance repr() { e } (actual type {type(instance_c20_popen).__name__}) has no specific fuzzer type, doing generic calls.', file=stderr)
    if skip_trivial_type(instance_c20_popen):
        print(f'Skipping deep diving on instance_c20_popen {type(instance_c20_popen)}', file=stderr)
    else:
        print(f'Instance instance_c20_popen (type {type(instance_c20_popen).__name__}) has no specific fuzzer, doing generic calls.', file=stderr)
        c20_popen_ops_generic_methods = []
        try:
            for c20_popen_ops_generic_attr_name in dir(instance_c20_popen):
                if c20_popen_ops_generic_attr_name.startswith('_'): continue
                try:
                    c20_popen_ops_generic_attr_val = getattr(instance_c20_popen, c20_popen_ops_generic_attr_name)
                    if callable(c20_popen_ops_generic_attr_val) and c20_popen_ops_generic_attr_name not in _FUSIL_METHOD_BLACKLIST: c20_popen_ops_generic_methods.append((c20_popen_ops_generic_attr_name, c20_popen_ops_generic_attr_val))
                except Exception: pass
        except Exception: c20_popen_ops_generic_methods = [] # Failed to get methods
        if c20_popen_ops_generic_methods:
            print(f'Found {len(c20_popen_ops_generic_methods)} callable methods for generic fuzzing of instance_c20_popen', file=stderr)
            for _i_c20_popen_ops_generic in range(min(len(c20_popen_ops_generic_methods), 15)):
                c20_popen_ops_generic_method_name_to_call, c20_popen_ops_generic_method_obj_to_call = choice(c20_popen_ops_generic_methods)
                # Conceptual call to generic method fuzzer
                if c20_popen_ops_generic_method_name_to_call not in _FUSIL_METHOD_BLACKLIST: callMethod(f'c20_popen_ops_generic_gen{_i_c20_popen_ops_generic}', instance_c20_popen, c20_popen_ops_generic_method_name_to_call)

if instance_c20_popen is not None and instance_c20_popen is not SENTINEL_VALUE:
    print(f"--- Fuzzing instance: instance_c20_popen (type hint: Popen, prefix: c20m) ---", file=stderr)
    if skip_trivial_type(instance_c20_popen):
        print(f'Skipping deep diving on instance_c20_popen {type(instance_c20_popen)}', file=stderr)
    # General method fuzzing for instance_c20_popen
    try:
        res_c20m1 = callMethod("c20m1", instance_c20_popen, "__getattribute__",
            LenBomb(),
        verbose=True)
    except Exception as _argexc_c20m1:
        print("[c20m1] call skipped (argument build failed):", repr(_argexc_c20m1), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c20_popen, '__getattribute__')
    except Exception as e_get_target_func:
        print(f"[c20m1] Failed to get attribute __getattribute__ from instance_c20_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(WrongTypeFile(),), name='c20m1___getattribute__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c20m1] Failed to create thread for __getattribute__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c20m1___getattribute__(target_func=target_func):
            print("Starting async task: async_call_c20m1___getattribute__", file=stderr)
            time.sleep(0.000751) # Small delay
            try:
                target_func(None)
            except Exception as e_async_call:
                print(f"[c20m1] Exception in async task async_call_c20m1___getattribute__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c20m1___getattribute__", file=stderr)
        fuzzer_async_tasks.append(async_call_c20m1___getattribute__)

    try:
        res_c20m2 = callMethod("c20m2", instance_c20_popen, "__new__",
            Exception('fuzzer_generated_exception'),
            '/tmp/fusil-fixtures/fusil_fixture.bin',
            tuple[weird_classes['weird_int']],
        verbose=True)
    except Exception as _argexc_c20m2:
        print("[c20m2] call skipped (argument build failed):", repr(_argexc_c20m2), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c20_popen, '__new__')
    except Exception as e_get_target_func:
        print(f"[c20m2] Failed to get attribute __new__ from instance_c20_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(True, r"\dnsHmZFqGIC", FilenoBomb()), name='c20m2___new__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c20m2] Failed to create thread for __new__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c20m2___new__(target_func=target_func):
            print("Starting async task: async_call_c20m2___new__", file=stderr)
            time.sleep(0.000697) # Small delay
            try:
                target_func(LyingLen(), r"ZYk\Z.xw..bEdJ\D.gtXOmb", weird_instances['weird_bytes_empty'])
            except Exception as e_async_call:
                print(f"[c20m2] Exception in async task async_call_c20m2___new__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c20m2___new__", file=stderr)
        fuzzer_async_tasks.append(async_call_c20m2___new__)

    try:
        res_c20m3 = callMethod("c20m3", instance_c20_popen, "__new__",
            inspect,
            '/tmp/fusil-fixtures/fusil_fixture.txt',
            ReprBomb(),
        verbose=True)
    except Exception as _argexc_c20m3:
        print("[c20m3] call skipped (argument build failed):", repr(_argexc_c20m3), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c20_popen, '__new__')
    except Exception as e_get_target_func:
        print(f"[c20m3] Failed to get attribute __new__ from instance_c20_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(list[weird_classes['weird_Counter']], "\xF2d\xB2\xE4\xDC", 15), name='c20m3___new__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c20m3] Failed to create thread for __new__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c20m3___new__(target_func=target_func):
            print("Starting async task: async_call_c20m3___new__", file=stderr)
            time.sleep(0.000118) # Small delay
            try:
                target_func(FilenoBomb(), TypeFlipIterator(), liar1)
            except Exception as e_async_call:
                print(f"[c20m3] Exception in async task async_call_c20m3___new__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c20m3___new__", file=stderr)
        fuzzer_async_tasks.append(async_call_c20m3___new__)

    try:
        res_c20m4 = callMethod("c20m4", instance_c20_popen, "__eq__",
            dict[weird_classes['weird_OrderedDict']],
        verbose=True)
    except Exception as _argexc_c20m4:
        print("[c20m4] call skipped (argument build failed):", repr(_argexc_c20m4), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c20_popen, '__eq__')
    except Exception as e_get_target_func:
        print(f"[c20m4] Failed to get attribute __eq__ from instance_c20_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=('/tmp/fusil-fixtures/fusil_fixture.bin',), name='c20m4___eq__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c20m4] Failed to create thread for __eq__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c20m4___eq__(target_func=target_func):
            print("Starting async task: async_call_c20m4___eq__", file=stderr)
            time.sleep(0.000233) # Small delay
            try:
                target_func([[1] * 10] * 10)
            except Exception as e_async_call:
                print(f"[c20m4] Exception in async task async_call_c20m4___eq__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c20m4___eq__", file=stderr)
        fuzzer_async_tasks.append(async_call_c20m4___eq__)

    try:
        res_c20m5 = callMethod("c20m5", instance_c20_popen, "__format__",
            "\x00" * 10,
        verbose=True)
    except Exception as _argexc_c20m5:
        print("[c20m5] call skipped (argument build failed):", repr(_argexc_c20m5), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c20_popen, '__format__')
    except Exception as e_get_target_func:
        print(f"[c20m5] Failed to get attribute __format__ from instance_c20_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(ReadBomb(),), name='c20m5___format__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c20m5] Failed to create thread for __format__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c20m5___format__(target_func=target_func):
            print("Starting async task: async_call_c20m5___format__", file=stderr)
            time.sleep(0.000416) # Small delay
            try:
                target_func(WrongTypeFile())
            except Exception as e_async_call:
                print(f"[c20m5] Exception in async task async_call_c20m5___format__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c20m5___format__", file=stderr)
        fuzzer_async_tasks.append(async_call_c20m5___format__)

    try:
        res_c20m6 = callMethod("c20m6", instance_c20_popen, "_send_signal",
            b"\xA9\x1D\x05\x66\xD3\x2E\xF3",
        verbose=True)
    except Exception as _argexc_c20m6:
        print("[c20m6] call skipped (argument build failed):", repr(_argexc_c20m6), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c20_popen, '_send_signal')
    except Exception as e_get_target_func:
        print(f"[c20m6] Failed to get attribute _send_signal from instance_c20_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(b"\xD3\x8C\x6A\x98\x60\x86\xCA\x20\xE6\xC2",), name='c20m6__send_signal')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c20m6] Failed to create thread for _send_signal: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c20m6__send_signal(target_func=target_func):
            print("Starting async task: async_call_c20m6__send_signal", file=stderr)
            time.sleep(0.000003) # Small delay
            try:
                target_func(None)
            except Exception as e_async_call:
                print(f"[c20m6] Exception in async task async_call_c20m6__send_signal: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c20m6__send_signal", file=stderr)
        fuzzer_async_tasks.append(async_call_c20m6__send_signal)

    try:
        res_c20m7 = callMethod("c20m7", instance_c20_popen, "__format__",
            False,
        verbose=True)
    except Exception as _argexc_c20m7:
        print("[c20m7] call skipped (argument build failed):", repr(_argexc_c20m7), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c20_popen, '__format__')
    except Exception as e_get_target_func:
        print(f"[c20m7] Failed to get attribute __format__ from instance_c20_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(HashBomb(),), name='c20m7___format__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c20m7] Failed to create thread for __format__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c20m7___format__(target_func=target_func):
            print("Starting async task: async_call_c20m7___format__", file=stderr)
            time.sleep(0.000653) # Small delay
            try:
                target_func(errback)
            except Exception as e_async_call:
                print(f"[c20m7] Exception in async task async_call_c20m7___format__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c20m7___format__", file=stderr)
        fuzzer_async_tasks.append(async_call_c20m7___format__)

    try:
        res_c20m8 = callMethod("c20m8", instance_c20_popen, "__init__",
            WrongTypeFile(),
        verbose=True)
    except Exception as _argexc_c20m8:
        print("[c20m8] call skipped (argument build failed):", repr(_argexc_c20m8), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c20_popen, '__init__')
    except Exception as e_get_target_func:
        print(f"[c20m8] Failed to get attribute __init__ from instance_c20_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=('/tmp/fusil-fixtures/fusil_fixture.bin',), name='c20m8___init__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c20m8] Failed to create thread for __init__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c20m8___init__(target_func=target_func):
            print("Starting async task: async_call_c20m8___init__", file=stderr)
            time.sleep(0.000825) # Small delay
            try:
                target_func(object())
            except Exception as e_async_call:
                print(f"[c20m8] Exception in async task async_call_c20m8___init__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c20m8___init__", file=stderr)
        fuzzer_async_tasks.append(async_call_c20m8___init__)

    try:
        res_c20m9 = callMethod("c20m9", instance_c20_popen, "__getattribute__",
            9,
        verbose=True)
    except Exception as _argexc_c20m9:
        print("[c20m9] call skipped (argument build failed):", repr(_argexc_c20m9), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c20_popen, '__getattribute__')
    except Exception as e_get_target_func:
        print(f"[c20m9] Failed to get attribute __getattribute__ from instance_c20_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=("EjoC/mF7tnDJL_xt_H8Aflg9vdfScDykdRAOcA-F245i6sALC/./-OKIW1flj82gTk02Y17_.1N/RilwJ2NJrTXU1n/TP/",), name='c20m9___getattribute__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c20m9] Failed to create thread for __getattribute__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c20m9___getattribute__(target_func=target_func):
            print("Starting async task: async_call_c20m9___getattribute__", file=stderr)
            time.sleep(0.000895) # Small delay
            try:
                target_func(weird_instances['weird_set_single'])
            except Exception as e_async_call:
                print(f"[c20m9] Exception in async task async_call_c20m9___getattribute__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c20m9___getattribute__", file=stderr)
        fuzzer_async_tasks.append(async_call_c20m9___getattribute__)

    try:
        res_c20m10 = callMethod("c20m10", instance_c20_popen, "poll",
            WrongTypeFile(),
        verbose=True)
    except Exception as _argexc_c20m10:
        print("[c20m10] call skipped (argument build failed):", repr(_argexc_c20m10), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c20_popen, 'poll')
    except Exception as e_get_target_func:
        print(f"[c20m10] Failed to get attribute poll from instance_c20_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(bytearray(b"abc\xe9\xff"),), name='c20m10_poll')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c20m10] Failed to create thread for poll: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c20m10_poll(target_func=target_func):
            print("Starting async task: async_call_c20m10_poll", file=stderr)
            time.sleep(0.000000) # Small delay
            try:
                target_func(LyingEq())
            except Exception as e_async_call:
                print(f"[c20m10] Exception in async task async_call_c20m10_poll: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c20m10_poll", file=stderr)
        fuzzer_async_tasks.append(async_call_c20m10_poll)

    try:
        res_c20m11 = callMethod("c20m11", instance_c20_popen, "__dir__",
        verbose=True)
    except Exception as _argexc_c20m11:
        print("[c20m11] call skipped (argument build failed):", repr(_argexc_c20m11), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c20_popen, '__dir__')
    except Exception as e_get_target_func:
        print(f"[c20m11] Failed to get attribute __dir__ from instance_c20_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c20m11___dir__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c20m11] Failed to create thread for __dir__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c20m11___dir__(target_func=target_func):
            print("Starting async task: async_call_c20m11___dir__", file=stderr)
            time.sleep(0.000181) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c20m11] Exception in async task async_call_c20m11___dir__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c20m11___dir__", file=stderr)
        fuzzer_async_tasks.append(async_call_c20m11___dir__)

    try:
        res_c20m12 = callMethod("c20m12", instance_c20_popen, "__str__",
        verbose=True)
    except Exception as _argexc_c20m12:
        print("[c20m12] call skipped (argument build failed):", repr(_argexc_c20m12), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c20_popen, '__str__')
    except Exception as e_get_target_func:
        print(f"[c20m12] Failed to get attribute __str__ from instance_c20_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c20m12___str__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c20m12] Failed to create thread for __str__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c20m12___str__(target_func=target_func):
            print("Starting async task: async_call_c20m12___str__", file=stderr)
            time.sleep(0.000105) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c20m12] Exception in async task async_call_c20m12___str__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c20m12___str__", file=stderr)
        fuzzer_async_tasks.append(async_call_c20m12___str__)

    try:
        res_c20m13 = callMethod("c20m13", instance_c20_popen, "kill",
        verbose=True)
    except Exception as _argexc_c20m13:
        print("[c20m13] call skipped (argument build failed):", repr(_argexc_c20m13), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c20_popen, 'kill')
    except Exception as e_get_target_func:
        print(f"[c20m13] Failed to get attribute kill from instance_c20_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(), name='c20m13_kill')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c20m13] Failed to create thread for kill: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c20m13_kill(target_func=target_func):
            print("Starting async task: async_call_c20m13_kill", file=stderr)
            time.sleep(0.000957) # Small delay
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c20m13] Exception in async task async_call_c20m13_kill: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c20m13_kill", file=stderr)
        fuzzer_async_tasks.append(async_call_c20m13_kill)

    try:
        res_c20m14 = callMethod("c20m14", instance_c20_popen, "__ne__",
            MagicMock(),
        verbose=True)
    except Exception as _argexc_c20m14:
        print("[c20m14] call skipped (argument build failed):", repr(_argexc_c20m14), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c20_popen, '__ne__')
    except Exception as e_get_target_func:
        print(f"[c20m14] Failed to get attribute __ne__ from instance_c20_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(errback,), name='c20m14___ne__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c20m14] Failed to create thread for __ne__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c20m14___ne__(target_func=target_func):
            print("Starting async task: async_call_c20m14___ne__", file=stderr)
            time.sleep(0.000757) # Small delay
            try:
                target_func(weird_instances['weird_Decimal_-2**63+1'])
            except Exception as e_async_call:
                print(f"[c20m14] Exception in async task async_call_c20m14___ne__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c20m14___ne__", file=stderr)
        fuzzer_async_tasks.append(async_call_c20m14___ne__)

    try:
        res_c20m15 = callMethod("c20m15", instance_c20_popen, "__gt__",
            IndexBomb(),
        verbose=True)
    except Exception as _argexc_c20m15:
        print("[c20m15] call skipped (argument build failed):", repr(_argexc_c20m15), file=stderr)

    target_func = None
    try:
        target_func = getattr(instance_c20_popen, '__gt__')
    except Exception as e_get_target_func:
        print(f"[c20m15] Failed to get attribute __gt__ from instance_c20_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)

    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(GrowingLen(),), name='c20m15___gt__')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c20m15] Failed to create thread for __gt__: {e_thread_create.__class__.__name__}", file=stderr)

    if target_func is not None:
        def async_call_c20m15___gt__(target_func=target_func):
            print("Starting async task: async_call_c20m15___gt__", file=stderr)
            time.sleep(0.000853) # Small delay
            try:
                target_func(-1190581131)
            except Exception as e_async_call:
                print(f"[c20m15] Exception in async task async_call_c20m15___gt__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
            print("Ending async task: async_call_c20m15___gt__", file=stderr)
        fuzzer_async_tasks.append(async_call_c20m15___gt__)

    print(f"--- Finished fuzzing instance: instance_c20_popen ---", file=stderr)

    del instance_c20_popen # Cleanup instance
    print("[c20] -explicit garbage collection for class instance-", file=stderr)
    collect()



print("--- Starting and Joining Fuzzer Threads ---", file=stderr)
for t_obj in fuzzer_threads_alive:
    try:
        print(f"Starting thread: {t_obj.name}", file=stderr)
        t_obj.start()
    except Exception as e_thread_start:
        print(f"Failed to start thread {t_obj.name}: {e_thread_start.__class__.__name__}", file=stderr)
for t_obj in fuzzer_threads_alive:
    try:
        print(f"Joining thread: {t_obj.name}", file=stderr)
        t_obj.join(timeout=1.0) # Add timeout to join
    except Exception as e_thread_join:
        print(f"Failed to join thread {t_obj.name}: {e_thread_join.__class__.__name__}", file=stderr)

print("--- Running Fuzzer Async Tasks ---", file=stderr)
async def main_async_fuzzer_tasks():
    if not fuzzer_async_tasks: return
    task_objects = [asyncio.to_thread(func) for func in fuzzer_async_tasks]
    await asyncio.gather(*task_objects, return_exceptions=True)

runner = asyncio.Runner()
try:
    runner.run(main_async_fuzzer_tasks())
except Exception as e_async_runner_run:
    print(f'Exception in async runner: {e_async_runner_run.__class__.__name__} {e_async_runner_run}')
finally:
    runner.close()

