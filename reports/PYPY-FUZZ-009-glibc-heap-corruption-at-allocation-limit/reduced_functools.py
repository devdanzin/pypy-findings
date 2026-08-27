try:
    _fusil_faulthandler.enable()
except Exception:
    pass
from gc import collect
from sys import stderr, path as sys_path
try:
    from string.templatelib import Interpolation, Template
except ImportError:
    import functools
except ImportError as _fusil_import_error:
    print("FUSIL: target module functools not importable (skipping):", repr(_fusil_import_error), file=stderr)
def skip_trivial_type(obj_instance_or_class):
        return True
import sys
from abc import ABCMeta
from collections import Counter, OrderedDict, deque
from queue import Queue
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
        return randint(0, large_num)
    def __eq__(self, other):
        return False
weird_instances = dict()
weird_classes = dict()
for cls in bases:
    class weird_cls(cls, metaclass=WeirdBase):
        def add(self, *args, **kwargs):
            pass
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
                frame.f_locals[self.var_name] = self.new_value
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
    if len(args) > 150:
        raise RecursionError("Fuzzer controlled depth")
    def __get__(self, obj, objtype=None):
            pass
    def __signature__(self):
        return (object,)
"""Exception-bomb objects: the protocol-level analogue of the OOM (allocation-failure) mode.
"""
_BOMB_EXCEPTIONS = (
)
class _BombBase:
    def __init__(self, max_delay=3, exc=MemoryError):
        self._calls = 0
        if self._calls > self._delay:
            raise _bomb_exc(self._exc)("fusil bomb")
    """__eq__ flips its answer every few calls, so a single C routine that compares this object
    equality relation change underneath it. __hash__ stays constant so it remains storable."""
    def __init__(self):
        self._period = _bomb_random.randint(2, 4)
_SUPERBOMB_DUNDERS = (
)
def _make_superbomb_slot(name):
    def _slot(self, *args, **kwargs):
            raise _bomb_exc()("fusil superbomb via %s" % name)
    def __new__(mcls, cname, bases, namespace):
        for _name in _SUPERBOMB_DUNDERS:
            namespace.setdefault(_name, _make_superbomb_slot(_name))
    """A data descriptor whose __get__/__set__ raise -- hits unguarded PyErr_Clear in getattr
    fallbacks when installed on a commonly-probed attribute name."""
    def __get__(self, obj, objtype=None):
        raise _bomb_exc()("fusil descriptor set")
    """Metaclass hash that succeeds at first (registration) then raises after a random delay --
    targets type-keyed registries (``PyDict_GetItem`` on a class key that changes hashability)."""
    def __new__(mcls, name, bases, namespace):
        if state[0] > state[1]:
            raise _bomb_exc()("fusil stateful hash")
_LYING_NUMERIC_SLOTS = (
)
def _make_lying_numeric_slot(name):
        return _bomb_random.choice(_LYING_NUMERIC_RETURNS)
class _LyingInplaceMeta(type):
    def __new__(mcls, cname, bases, namespace):
        for _name in _LYING_NUMERIC_SLOTS:
            namespace.setdefault(_name, _make_lying_numeric_slot(_name))
    """Every numeric slot (forward / reflected / in-place) succeeds but returns a random UNEXPECTED
    it reaches the number-protocol slot instead of detonating during arg handling."""
BOMB_CLASS_NAMES = [
]
class Liar1:
    def __eq__(self, other):
        return True
        for attr in dir(other):
            try: other.__dict__[attr] = errback
            except: pass
def compare_results(a, b):
    if isinstance(a, types.FunctionType) and a.__name__ == '<lambda>' and \
       isinstance(b, types.FunctionType) and b.__name__ == '<lambda>':
        return True
SENTINEL_VALUE = object()
def callMethod(prefix, obj_to_call, method_name, *arguments, verbose=True):
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
    collect()
def callFunc(prefix, func_name_str, *arguments, verbose=True):
    return callMethod(prefix, functools, func_name_str, *arguments, verbose=verbose)
try:
    res_f1 = callFunc("f1", "_lt_from_gt",
    verbose=True)
except Exception as _argexc_f1:
    print("[f1] call skipped (argument build failed):", repr(_argexc_f1), file=stderr)
target_func = None
try:
    target_func = getattr(fuzz_target_module, '_lt_from_gt')
except Exception as e_get_target_func:
    print(f"[f1] Failed to get attribute _lt_from_gt from fuzz_target_module: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)
    try:
        fuzzer_threads_alive.append(thread_obj)
    except Exception as e_thread_create:
        print(f"[f1] Failed to create thread for _lt_from_gt: {e_thread_create.__class__.__name__}", file=stderr)
if target_func is not None:
    def async_call_f1__lt_from_gt(target_func=target_func):
        try:
            target_func(ReprBomb())
        except Exception as e_async_call:
            print(f"[f1] Exception in async task async_call_f1__lt_from_gt: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
try:
    res_f2 = callFunc("f2", "_lt_from_le",
    verbose=True)
except Exception as _argexc_f2:
    print("[f2] call skipped (argument build failed):", repr(_argexc_f2), file=stderr)
    def async_call_f2__lt_from_le(target_func=target_func):
        try:
            target_func(memoryview(bytearray(b"abc\xe9\xff")))
        except Exception as e_async_call:
            print(f"[f2] Exception in async task async_call_f2__lt_from_le: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
try:
    res_f3 = callFunc("f3", "_c3_mro",
        weird_classes['weird_int'],
    verbose=True)
except Exception as _argexc_f3:
    print("[f3] call skipped (argument build failed):", repr(_argexc_f3), file=stderr)
    def async_call_f3__c3_mro(target_func=target_func):
        try:
            target_func("\uDC80")
        except Exception as e_async_call:
            print(f"[f3] Exception in async task async_call_f3__c3_mro: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
if target_func is not None:
    try:
        fuzzer_threads_alive.append(thread_obj)
    except Exception as e_thread_create:
        try:
            target_func(None)
        except Exception as e_async_call:
            print(f"[f4] Exception in async task async_call_f4__le_from_lt: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
try:
    res_f5 = callFunc("f5", "_lru_cache_wrapper",
        905458644924897,
        2759,
        weird_classes['weird_complex'],
        r"TB.ydvzD.o\B+rDjuT",
    verbose=True)
except Exception as _argexc_f5:
    print("[f5] call skipped (argument build failed):", repr(_argexc_f5), file=stderr)
if target_func is not None:
    def async_call_f5__lru_cache_wrapper(target_func=target_func):
        try:
            target_func(errback, False, EqBomb(), -12)
        except Exception as e_async_call:
            print(f"[f5] Exception in async task async_call_f5__lru_cache_wrapper: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
try:
    res_f7 = callFunc("f7", "_compose_mro",
    verbose=True)
except Exception as _argexc_f7:
    print("[f7] call skipped (argument build failed):", repr(_argexc_f7), file=stderr)
