import threading, argparse, time, atomics

result = 0
atomic_result: atomics.INTEGRAL = atomics.atomic(4, atomics.INT)

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--sum-to', type=int, default=2 * 10 ** 9)
    parser.add_argument('--atomic', type=bool, default=True)
    parser.add_argument('--no-protection', type=bool, default=True)
    parser.add_argument('--mutex', type=bool, default=True)
    return parser.parse_args()


class UnprotectedThread(threading.Thread):
    def __init__(self, max_actions: int = 10 ** 9) -> None:
        super(UnprotectedThread, self).__init__()
        self.max_actions = max_actions
        
    def run(self) -> None:
        global result
        for _ in range(self.max_actions):
            result += 1


class MutexThread(threading.Thread):
    def __init__(self, lock: threading.Lock, max_actions: int = 10 ** 9) -> None:
        super(MutexThread, self).__init__()
        self.lock = lock
        self.max_actions = max_actions
        
    def run(self) -> None:
        global result
        for _ in range(self.max_actions):
            self.lock.acquire()
            result += 1
            self.lock.release()


class AtomicThread(threading.Thread):
    def __init__(self, max_actions: int = 10 ** 9) -> None:
        super(AtomicThread, self).__init__()
        self.max_actions = max_actions
        
    def run(self) -> None:
        global atomic_result
        for _ in range(self.max_actions):
            atomic_result.inc()


def clear_setup() -> None:
    global result
    result = 0
    

def run_experiment(thread_class, **kwargs) -> tuple[float, int]:
    global result
    thread_1 = thread_class(**kwargs)
    thread_2 = thread_class(**kwargs)
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
            thread_class=UnprotectedThread,
            max_actions=args.sum_to // 2
        )
        print('Running time: %0.4f, result: %d' % (running_time, result))
        clear_setup()
    
    if args.mutex:
        print('Start execution of the experiment with mutex...')
        running_time, result = run_experiment(
            thread_class=MutexThread,
            max_actions=args.sum_to // 2,
            lock=threading.Lock()
        )
        print('Running time: %0.4f, result: %d' % (running_time, result))
        clear_setup()
        
    if args.atomic:
        print('Start execution of the experiment without protection...')
        running_time, result = run_experiment(
            thread_class=AtomicThread,
            max_actions=args.sum_to // 2
        )
        print('Running time: %0.4f, result: %d' % (running_time, atomic_result.fetch_inc()))
        clear_setup()
        