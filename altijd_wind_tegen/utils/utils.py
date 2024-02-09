from time import perf_counter


def timit(func):
    def wrapper(*args, **kwargs):
        start_time = perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {perf_counter() - start_time:.5f} seconds to execute")
        return result

    return wrapper
