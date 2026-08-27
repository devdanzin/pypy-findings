try:
    import faulthandler as _fusil_faulthandler
    _fusil_faulthandler.enable()
except Exception:
    pass
from threading import Thread
try:
    from string.templatelib import Interpolation, Template
except ImportError:
    import multiprocessing.popen_fork
def skip_trivial_type(obj_instance_or_class):
    has__decimal = False
class ShiftyEq:
    """__eq__ flips its answer every few calls, so a single C routine that compares this object
    equality relation change underneath it. __hash__ stays constant so it remains storable."""
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
    return result
def callFunc(prefix, func_name_str, *arguments, verbose=True):
    return callMethod(prefix, multiprocessing.popen_fork, func_name_str, *arguments, verbose=verbose)
fuzzer_threads_alive = []
try:
    instance_c1_popen = callFunc('c1_init', 'Popen',
        False,
      )
except Exception as e_instantiate:
    instance_c16_popen = callFunc('c16_init', 'Popen',
      )
    if skip_trivial_type(instance_c16_popen):
        try:
                try:
                    if callable(c16_popen_ops_generic_attr_val) and c16_popen_ops_generic_attr_name not in _FUSIL_METHOD_BLACKLIST: c16_popen_ops_generic_methods.append((c16_popen_ops_generic_attr_name, c16_popen_ops_generic_attr_val))
                except Exception: pass
        except Exception: c16_popen_ops_generic_methods = [] # Failed to get methods
    try:
        res_c16m1 = callMethod("c16m1", instance_c16_popen, "kill",
        verbose=True)
    except Exception as _argexc_c16m1:
        try:
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            try:
                target_func(int)
            except Exception as e_async_call:
                print(f"[c17m6] Exception in async task async_call_c17m6_poll: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
try:
    instance_c18_popen = callFunc('c18_init', 'Popen',
        ShiftyEq(),
      )
except Exception as e_instantiate:
        try:
                try:
                    if callable(c18_popen_ops_generic_attr_val) and c18_popen_ops_generic_attr_name not in _FUSIL_METHOD_BLACKLIST: c18_popen_ops_generic_methods.append((c18_popen_ops_generic_attr_name, c18_popen_ops_generic_attr_val))
                except Exception: pass
        except Exception: c18_popen_ops_generic_methods = [] # Failed to get methods
if instance_c18_popen is not None and instance_c18_popen is not SENTINEL_VALUE:
    if skip_trivial_type(instance_c18_popen):
            print(f"[c18m2] Failed to create thread for __reduce__: {e_thread_create.__class__.__name__}", file=stderr)
    try:
        target_func = getattr(instance_c18_popen, '__init__')
    except Exception as e_get_target_func:
        try:
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c18m3] Failed to create thread for __init__: {e_thread_create.__class__.__name__}", file=stderr)
    try:
        target_func = getattr(instance_c18_popen, '_send_signal')
    except Exception as e_get_target_func:
        print(f"[c18m8] Failed to get attribute _send_signal from instance_c18_popen: {e_get_target_func.__class__.__name__} {e_get_target_func}", file=stderr)
    if target_func is not None:
        try:
            thread_obj = Thread(target=target_func, args=(4,), name='c18m8__send_signal')
        except Exception as e_thread_create:
            try:
                target_func()
            except Exception as e_async_call:
                print(f"[c18m14] Exception in async task async_call_c18m14___getstate__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
    try:
        res_c18m15 = callMethod("c18m15", instance_c18_popen, "__reduce__",
        verbose=True)
    except Exception as _argexc_c18m15:
        print("[c18m15] call skipped (argument build failed):", repr(_argexc_c18m15), file=stderr)
try:
    instance_c19_popen = callFunc('c19_init', 'Popen',
      )
except Exception as e_instantiate:
        try:
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
            print(f"[c20m11] Failed to create thread for __dir__: {e_thread_create.__class__.__name__}", file=stderr)
for t_obj in fuzzer_threads_alive:
    try:
        t_obj.start()
    except Exception as e_thread_start:
        print(f"Failed to start thread {t_obj.name}: {e_thread_start.__class__.__name__}", file=stderr)
async def main_async_fuzzer_tasks():
    if not fuzzer_async_tasks: return
