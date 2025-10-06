# bench_vex.py
import time
from vex import Vex

def benchmark_init():
  start = time.time()
  for _ in range(1000):
    Vex(output_bits=256, key=b"test_key")
  return (time.time() - start) / 1000 * 1e6  # µs

def benchmark_map_data():
  vex = Vex(output_bits=256, key=b"test_key")
  start = time.time()
  for _ in range(1000):
    vex.map_data(b"test_data")
  return (time.time() - start) / 1000 * 1e6  # µs

if __name__ == "__main__":
  init_time = benchmark_init()
  map_data_time = benchmark_map_data()
  print(f"Init time: {init_time:.3f} µs")
  print(f"Map data time: {map_data_time:.3f} µs")