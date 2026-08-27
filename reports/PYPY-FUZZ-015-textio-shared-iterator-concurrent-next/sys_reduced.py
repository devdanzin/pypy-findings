try:
    _fusil_faulthandler.enable()
except Exception:
    pass
from random import choice, randint, sample, seed
from sys import stderr, path as sys_path
from os.path import dirname
try:
    from string.templatelib import Interpolation, Template
except ImportError as _fusil_import_error:
    print("FUSIL: target module sys not importable (skipping):", repr(_fusil_import_error), file=stderr)
def skip_trivial_type(obj_instance_or_class):
    if type(obj_instance_or_class) in TRIVIAL_TYPES:
        return True

import sys
from abc import ABCMeta
from collections import Counter, OrderedDict, deque
from queue import Queue
from string import printable
try:
    from _decimal import Decimal

except ImportError:
    from decimal import Decimal
    has__decimal = False
sequences = [Queue, deque, frozenset, list, set, str, tuple]
bytes_ = [bytearray, bytes]
numbers = [Decimal, complex, float, int]
dicts = [Counter, OrderedDict, dict]
bases = sequences + bytes_ + numbers + dicts + [object]

class WeirdBase(ABCMeta):
    def __hash__(self):
        return False
weird_instances = dict()
weird_classes = dict()
for cls in bases:
    class weird_cls(cls, metaclass=WeirdBase):
        def add(self, *args, **kwargs):
            pass
        def decode(self, *args, **kwargs):
            return ""
    weird_classes[f"weird_{cls.__name__}"] = weird_cls
tricky_strs = (
)
max_str_digits_adjustment = 1 if has__decimal else -1
_default_max_str_digits = getattr(sys, "int_info", None)
_default_max_str_digits = getattr(_default_max_str_digits, "default_max_str_digits", 4300)
big_int_for_decimal = 10 ** (_default_max_str_digits + max_str_digits_adjustment)
for cls in sequences:
    weird_instances[f"weird_{cls.__name__}_range"] = weird_classes[f"weird_{cls.__name__}"](
    )
    weird_instances[f"weird_{cls.__name__}_printable"] = weird_classes[f"weird_{cls.__name__}"](
    )
    weird_instances[f"weird_{cls.__name__}_special"] = weird_classes[f"weird_{cls.__name__}"](
    )
    weird_instances[f"weird_{cls.__name__}_bytes"] = weird_classes[f"weird_{cls.__name__}"](
    )
for cls in numbers:
    weird_instances[f"weird_{cls.__name__}_sys_maxsize"] = weird_classes[f"weird_{cls.__name__}"](
    )
    weird_instances[f"weird_{cls.__name__}_sys_maxsize_minus_one"] = weird_classes[
        f"weird_{cls.__name__}"
    ](-sys.maxsize)
    weird_instances[f"weird_{cls.__name__}_2**63-1"] = weird_classes[f"weird_{cls.__name__}"](
    )
    weird_instances[f"weird_{cls.__name__}_2**63+1"] = weird_classes[f"weird_{cls.__name__}"](
    )
    weird_instances[f"weird_{cls.__name__}_-2**63+1"] = weird_classes[f"weird_{cls.__name__}"](
    )
    weird_instances[f"weird_{cls.__name__}_-2**63"] = weird_classes[f"weird_{cls.__name__}"](
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
    )
    def __del__(self):
        try:
            print(
            )
            if self.var_name in frame.f_locals:
                setattr(frame.f_locals[instance_or_class_str], attr_str, self.new_value)
        except Exception as e:
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

all_types = (
)
big_union = reduce(or_, all_types, int)
import inspect
tricky_cell = types.CellType(None)
tricky_simplenamespace = types.SimpleNamespace(dummy=None, cell=tricky_cell)
try:
    tricky_capsule = types.CapsuleType
except AttributeError:
    tricky_capsule = None
tricky_module = types.ModuleType("tricky_module", "docs")
try:
    tricky_genericalias = types.GenericAlias(list, (int,))
except AttributeError:
    tricky_genericalias = None
tricky_dict = {}
if tricky_capsule:
    tricky_dict[tricky_capsule] = tricky_cell
def tricky_function(*args, **kwargs):
    if len(args) > 150:
        raise RecursionError("Fuzzer controlled depth")
tricky_lambda = lambda *args, **kwargs: tricky_lambda(*args, **kwargs)
tricky_code = tricky_lambda.__code__
class TrickyDescriptor:
    def __get__(self, obj, objtype=None):
        return self
    def __set__(self, obj, value):
            pass
class TrickyMeta(type):
    def __signature__(self):
        raise AttributeError("Signature denied by TrickyMeta")
        # return super().__mro_entries__(bases)
class TrickyClass(metaclass=TrickyMeta):
    def __getattr__(self, name):
        if name == "crash_on_getattr":
            raise ValueError("getattr manipulated")
        return self

try:
    tricky_frame = inspect.currentframe()
    if tricky_frame:  # currentframe() can be None
        tricky_frame.f_locals.update(tricky_dict)
# Writing f_locals is a CPython frame detail (PEP 667 in 3.13); on interpreters where
except Exception:
    tricky_traceback = e.__traceback__

tricky_list_with_cycle = [[]] * 6 + []
if tricky_list_with_cycle[0] and tricky_list_with_cycle[0][0] is tricky_list_with_cycle:
    tricky_list_with_cycle[0][0].append(tricky_list_with_cycle)
# path overflows its C/Rust stack instead. Construction is cheap -- the recursion fires only
class _TrickyRecur:
    def __init__(self, name):
        self.partner = self  # rebound to a partner below for mutual recursion
    def __eq__(self, other):
        return self.partner == other
try:
    _tricky_ga = _TrickyGAT
except Exception:
    _tricky_ga = list
    for _ in range(80):
        _tricky_ga = list[_tricky_ga]
except Exception:
    tricky_deep_genericalias = None
"""Exception-bomb objects: the protocol-level analogue of the OOM (allocation-failure) mode.
slot (``__hash__``, ``__eq__``, ``__index__``, ``__len__``, ``__iter__``, ``__repr__``, ...)
"""
_BOMB_EXCEPTIONS = (
    SystemError,
)
class _BombBase:
    def __init__(self, max_delay=3, exc=MemoryError):
        self._calls = 0

    """A hostile iterable whose ``__length_hint__`` lies (huge / zero / negative) and whose
    ``b"".join()`` / ``set()`` / ``[*it]`` / ``PySequence_Tuple`` / ``_PyList_Extend`` -- can
    over-read or write past the presized buffer when the real yield count disagrees."""
    def __init__(self):
        self._hint = _bomb_random.choice([0, 1, -1, 1 << 16, 1 << 20])
        def _gen():
                if i == 1:
                    data.clear()
# storing under a cached __hash__, specializing on the first element's type -- writes past the
    """__len__ under-reports on its first read (small presize) then reports a much larger size,
    buffer-preallocation class; complements LyingLen, which only over-reports)."""
    def __init__(self):
        return index
        if self._calls <= self._delay:
            return 0
    """Yields a consistent type (ints) for a few items, then flips to an incompatible type
    (str / None / float / a bare object) mid-stream, feeding C reducers that may specialize on
    a wrong type after the fast-path has committed."""
_SUPERBOMB_DUNDERS = (
)
def _make_superbomb_slot(name):
    def _slot(self, *args, **kwargs):
            raise _bomb_exc()("fusil superbomb via %s" % name)
class _SuperBombMeta(type):
        for _name in _SUPERBOMB_DUNDERS:
            namespace.setdefault(_name, _make_superbomb_slot(_name))
_LYING_NUMERIC_SLOTS = (
    "__rmatmul__",
)
def _make_lying_numeric_slot(name):
        return _bomb_random.choice(_LYING_NUMERIC_RETURNS)
BOMB_TYPE_NAMES = [
]
def errback(*args, **kw):
    raise ValueError('errback called')

    if isinstance(a, types.FunctionType) and a.__name__ == '<lambda>' and \
       isinstance(b, types.FunctionType) and b.__name__ == '<lambda>':
        imag_match = (a.imag == b.imag) or (a_imag_nan and b_imag_nan)
    try:
            result = func_to_run(*arguments)
    except (Exception, SystemExit, KeyboardInterrupt) as err:
        try:
            errmsg = repr(err)
        except Exception as e_repr:
            try:
                _repr_detail = str(e_repr)
            except Exception:
                _repr_detail = '<unprintable>'
        result = SENTINEL_VALUE
fuzz_target_module = sys
import threading as _tsan_threading
import gc as _tsan_gc
import weakref as _tsan_weakref
import operator as _tsan_operator
import types as _tsan_types
print("[TSAN] entering concurrency-stress region", file=stderr)
print('[TSAN-MANIFEST] {"ext_iterators": 3, "func_count": 40, "iter_off": 6, "iterators": ["str", "bytes", "list", "tuple", "dict", "range", "itertools.count", "struct.iter_unpack"], "iters": 200, "kind": "tsan-provenance", "module": "sys", "mutate_callables": false, "mutate_state": false, "mutate_types": false, "ops": ["a:read-churn", "b:method", "c:module-func", "d:attr-dict", "e:weakref", "f:container-mutate", "g:gc", "h:shared-iter", "i:read-while-mutate"], "plugin_factories": [], "roles": {"0": "writer", "1": "reader", "2": "both"}, "shared_args": ["list", "dict", "set", "bytearray"], "shared_classes": [], "shared_kind": "target-objects", "shared_objects": ["__stdout__", "pypy_version_info", "__stdin__"], "shared_objects_only": false, "v": 1, "weird_subclasses": [], "workers_per_obj": 4}', file=stderr)
if getattr(sys, "_is_gil_enabled", lambda: True)():
    print("[CSTRESS] note: GIL enabled; running serialised (concurrency-stress still exercises threading teardown/re-entrancy)", file=stderr)
_tsan_shared_args = [[1, 2, 3], {"k": 1}, {1, 2, 3}, bytearray(b"fusil")]
_tsan_unsafe = frozenset(('_exit', 'abort', 'exec', 'execl', 'execle', 'execlp', 'execlpe', 'execv', 'execve', 'execvp', 'execvpe', 'fork', 'forkpty', 'popen', 'posix_spawn', 'posix_spawnp', 'register_at_fork', 'spawn', 'spawnl', 'spawnle', 'spawnlp', 'spawnlpe', 'spawnv', 'spawnve', 'spawnvp', 'spawnvpe', 'system'))
_MUTATE_STATE = False
class _TsanTypeBaseA:
    _tsan_base_id = 0
    _tsan_base_id = 1
class _TsanSharedType(_TsanTypeBaseA):
    def _tm0(self):
        return 0
        return 1
_MUTATE_CALLABLES = False
def _tsan_make_closure(_seed=0):
    _closed = _seed
    def _fn(_a=0, _b=0):
        return _closed + _a + _b
    return _fn
def _tsan_alt_closure():
    def _fn(_a, _b, _c):  # different arity, still 1 freevar -> __code__-swap-compatible
        return _closed
    return _fn
_tsan_shared_fn = _tsan_make_closure()
_tsan_obj_factories = []
_tsan_obj_factories.append(lambda: getattr(fuzz_target_module, '__stdin__'))
_TSAN_MAX_SHARED = 3
_tsan_shared = []
for _of in _tsan_obj_factories:
    if len(_tsan_shared) >= _TSAN_MAX_SHARED:
        break
    try:
        _tsan_shared.append(_of())
    except Exception:
        pass
_tsan_shared.append(fuzz_target_module)
if not _tsan_shared:
    _tsan_shared = [fuzz_target_module]
_tsan_iter_factories = [
]
_tsan_iter_factories.append(lambda: iter(getattr(fuzz_target_module, '__stdin__')))
_tsan_iter_ok = []
_TSAN_SKIP_ITER = (
    _tsan_types.AsyncGeneratorType,
)
for _f in _tsan_iter_factories:
    try:
        if isinstance(_it0, _TSAN_SKIP_ITER):
            continue
    except Exception:
        pass
_WORKERS_PER_OBJ = 4
_ITERS = 200
_tsan_total = len(_tsan_shared) * _WORKERS_PER_OBJ
_tsan_barrier = _tsan_threading.Barrier(_tsan_total)
def _tsan_worker(_idx, _wid):
    _obj = _tsan_shared[_idx]
    _bag = _tsan_shared_args[_idx % len(_tsan_shared_args)]
    _role = _wid % 3
    # Concurrent-mutation state (op b curated tier + op j), cached once per worker;
    for _i in range(_ITERS):
        if _role != 1:
            for _op in (repr, hash, list, len, bool, iter, str):
                try:
                    _op(_obj)
                except Exception:
                    pass
            try:
                    if callable(_m):
                        _off = (_wid + _i) % len(_tsan_call_args)
                    if callable(_m):
                        _m(*_tsan_shared_args[: (_i % 3)])
            except Exception:
                pass
            try:
                getattr(fuzz_target_module,
                        _tsan_funcs[(_wid + _i) % len(_tsan_funcs)])(_obj)
            except Exception:
                pass
        try:
            if _role != 0:
                    delattr(_obj, "_tsan_a%d" % (_i % 4))
            if _role != 1:
                getattr(_obj, "_tsan_a%d" % (_wid % 4), None)
        except Exception:
            try:
                    _bag.append(_i)
            except Exception:
                pass
                if _role != 1:
                    try:
                        _tsan_operator.length_hint(_it, 0)
                    except Exception:
                        pass
_tsan_threads = []
for _idx in range(len(_tsan_shared)):
    for _wid in range(_WORKERS_PER_OBJ):
        _tsan_threads.append(_tsan_threading.Thread(
            target=_tsan_worker, args=(_idx, _wid), name="tsan_%d_%d" % (_idx, _wid)))
for _t in _tsan_threads:
    _t.start()
for _t in _tsan_threads:
    _t.join()
