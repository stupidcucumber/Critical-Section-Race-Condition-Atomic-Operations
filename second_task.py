import threading, argparse, time, atomics
from typing import Callable

result = 0
atomic_result: atomics.INTEGRAL = atomics.atomic(4, atomics.INT)

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--sum-to', type=int, default=2 * 10 ** 9)
    parser.add_argument('--atomic', type=bool, default=True)
    parser.add_argument('--no-protection', type=bool, default=True)
    parser.add_argument('--mutex', type=bool, default=True)
    return parser.parse_args()


def clear_setup() -> None:
    global result
    result = 0


def no_protection_task(max: int = 2 * 10 ** 9) -> None:
    global result
    while result < max:
        result += 1
        
        
def mutex_task(lock: threading.Lock, max: int = 2 * 10 ** 9) -> None:
    global result
    while result < max:
        lock.acquire()
        result += 1
        lock.release()


def atomic_task(max: int = 2 * 10 ** 9) -> None:
     global atomic_result
     while atomic_result.fetch_inc() < max:
        atomic_result.inc()
    

def run_experiment(target: Callable, **kwargs) -> tuple[float, int]:
    thread_1 = threading.Thread(
        target=target,
        kwargs=kwargs
    )
    thread_2 = threading.Thread(
        target=target,
        kwargs=kwargs
    )
    start = time.perf_counter()
    thread_1.start()
    thread_2.start()
    thread_1.join()
    thread_2.join()
    end = time.perf_counter()
    return end - start, result


if __name__ == '__main__':
    args = parse_arguments()
    
    if args.no_protection:
        print('Start execution of the experiment without protection...')
        running_time, result = run_experiment(
            target=no_protection_task,
            max=args.sum_to
        )
        print('Running time: %0.4f, result: %d' % (running_time, result))
        clear_setup()
    
    if args.mutex:
        print('Start execution of the experiment with mutex...')
        running_time, result = run_experiment(
            target=mutex_task,
            max=args.sum_to,
            lock=threading.Lock()
        )
        print('Running time: %0.4f, result: %d' % (running_time, result))
        clear_setup()
        
    if args.atomic:
        print('Start execution of the experiment without protection...')
        running_time, result = run_experiment(
            target=atomic_task,
            max=args.sum_to
        )
        print('Running time: %0.4f, result: %d' % (running_time, result))
        clear_setup()
        