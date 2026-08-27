from threading import Thread
try:
    import importlib.machinery
except ImportError as _fusil_import_error:
    from decimal import Decimal
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
    return callMethod(prefix, importlib.machinery, func_name_str, *arguments, verbose=verbose)
fuzzer_threads_alive = []
try:
    instance_c20_sourcefileloader = callFunc('c20_init', 'SourceFileLoader',
        -658591015,
        b"\x43\xE6\x2E\x53\xF6\x71\x67\x3C\x96\x57\x14\x5F\x3B\xB6\xB7",
      )
except Exception as e:
    print(f"--- (Depth 0) Error calling repr() prefix: c20_sourcefileloader_ops) ---", file=stderr)
if instance_c20_sourcefileloader is not None:
    try:
        res_c20m4 = callMethod("c20m4", instance_c20_sourcefileloader, "get_filename",
        verbose=True)
    except Exception as _argexc_c20m4:
            try:
                target_func(liar1)
            except Exception as e_async_call:
                print(f"[c20m10] Exception in async task async_call_c20m10_create_module: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
    try:
        res_c20m11 = callMethod("c20m11", instance_c20_sourcefileloader, "source_to_code",
        verbose=True)
    except Exception as _argexc_c20m11:
        target_func = getattr(instance_c20_sourcefileloader, 'source_to_code')
        try:
            thread_obj = Thread(target=target_func, args=(memoryview(bytearray(b"abc\xe9\xff")), b"\xC1\x92\xDF"), name='c20m11_source_to_code')
            fuzzer_threads_alive.append(thread_obj)
        except Exception as e_thread_create:
                print(f"[c20m14] Exception in async task async_call_c20m14___lt__: {e_async_call.__class__.__name__} {e_async_call}", file=stderr)
for t_obj in fuzzer_threads_alive:
    try:
        t_obj.start()
    except Exception as e_thread_join:
        print(f"Failed to join thread {t_obj.name}: {e_thread_join.__class__.__name__}", file=stderr)
