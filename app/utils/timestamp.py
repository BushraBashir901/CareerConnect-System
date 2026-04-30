import time

def start_timer():
    return time.perf_counter()


def end_timer(start, label):
    print(f"{label}: {time.perf_counter() - start:.3f} sec")