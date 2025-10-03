# bench_vex.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
import numpy as np
from blake3 import blake3
from vex import Vex
try:
  from oqs import Signature
except ImportError:
  Signature = None

vex = Vex(buffer_size=1000000, prime_base=2, nesting_depth=8, output_bits=256, prime_count=200)
blake3_data = {size: b"0" * size for size in [1000, 10000, 100000]}

def run_benchmark(func, input_size, iterations=10):
  times = []
  for _ in range(iterations):
    start = time.perf_counter()
    result = func(input_size)
    times.append(time.perf_counter() - start)
  mean = np.mean(times) * 1e6
  stddev = np.std(times) * 1e6
  return mean, stddev, result

def bench_blake3(input_size):
  return blake3(blake3_data[input_size]).digest()

def bench_sphincs(data):
  if Signature is None:
    return None
  sphincs = Signature('SPHINCS+-SHA2-256s-simple')
  sk = sphincs.keypair()
  sig = sphincs.sign(data)
  sphincs.verify(data, sig, sk[1])
  return None

def bench_blake3_sphincs(input_size):
  blake3_start = time.perf_counter()
  hash_result = blake3(blake3_data[input_size]).digest()
  blake3_time = (time.perf_counter() - blake3_start) * 1e6
  sphincs_start = time.perf_counter()
  bench_sphincs(blake3_data[input_size])
  sphincs_time = (time.perf_counter() - sphincs_start) * 1e6
  return blake3_time, sphincs_time

def bench_vex(input_size):
  return vex.map_data(blake3_data[input_size])

if __name__ == "__main__":
  sizes = [1000, 10000, 100000]
  for size in sizes:
    mean, stddev, _ = run_benchmark(bench_vex, size)
    print(f"Size {size}: Vex {mean:.2f} µs (stddev {stddev:.2f})")
    blake3_mean, blake3_stddev, _ = run_benchmark(bench_blake3, size)
    total_mean, total_stddev, (blake3_time, sphincs_time) = run_benchmark(bench_blake3_sphincs, size)
    print(f"Size {size}: BLAKE3+SPHINCS+ {total_mean:.2f} µs (stddev {total_stddev:.2f}), BLAKE3 {blake3_time:.2f} µs, SPHINCS+ {sphincs_time:.2f} µs")
