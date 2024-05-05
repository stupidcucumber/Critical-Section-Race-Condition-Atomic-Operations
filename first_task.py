import itertools
import numpy as np
import time, argparse
from concurrent.futures import ThreadPoolExecutor


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', type=int, default=10)
    parser.add_argument('-k', type=int, default=10)
    parser.add_argument('-m', type=int, default=10)
    parser.add_argument('--workers', type=int, default=10,
                        help='The number of workers must be between 1 and n.')
    parser.add_argument('--n-experiments', type=int, default=100)
    return parser.parse_args()


def multiply_vectors(vectors) -> np.float32:
    with ThreadPoolExecutor(max_workers=len(vectors[0])) as executor:
        results = list(executor.map(
            lambda x, y: x * y,
            *vectors
        ))
    return sum(results)


def multiply_matrices(matrixA: np.ndarray, matrixB: np.ndarray, num_workers: int) -> np.ndarray:
    n, k = matrixA.shape[0], matrixB.shape[1]
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        results = list(executor.map(
            multiply_vectors,
            itertools.product(matrixA, matrixB.T)
        ))
    return np.asarray(results).reshape(n, k)


if __name__ == '__main__':
    args = parse_arguments()
    np.random.seed(0)
    times = []
    for _ in range(args.n_experiments):
        matrixA = np.random.randint(-100, 100, size=(args.n, args.m))
        matrixB = np.random.randint(-100, 100, size=(args.m, args.k))

        start = time.perf_counter()
        results = multiply_matrices(matrixA=matrixA, matrixB=matrixB, num_workers=args.workers)
        end = time.perf_counter()
        times.append(end - start)
    print('On average multiplying was: ', np.mean(times))
