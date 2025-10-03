# vex.py
from ctypes import c_uint32
from typing import List, Optional

class Vex:
  def __init__(self, buffer_size: int = 1000000, prime_base: int = 2, nesting_depth: int = 8, output_bits: int = 256, prime_count: int = 200, key: Optional[bytes] = None):
    self.buffer_size = min(buffer_size, prime_count)
    self.prime_base = max(2, prime_base)
    self.nesting_depth = max(1, min(nesting_depth, 16))
    self.output_bits = max(64, min(output_bits, 256))
    self.prime_count = max(100, min(prime_count, 1000))
    self.count = min(self.prime_count, 1000)
    self.indices = self._generate_primes(self.prime_count, key)
    self.output_size = max(2, self.output_bits // 32)
    table_size = max(2, 8 if output_bits <= 256 else 16)
    self.map_table = ((c_uint32 * table_size * table_size) * self.output_size)()
    key_val = sum(key) if key else 0
    for j in range(self.output_size):
      for i in range(table_size):
        for k in range(table_size):
          self.map_table[j][i][k] = c_uint32(pow(self.indices[i % self.count], (k + j + 1) % self.count + 1, 0xFFFFFFFF) ^ ((i * self.indices[(k + j + 1) % self.count]) ^ (i << (7 + j)) ^ (k >> (2 + j)) ^ (self.indices[i % self.count] % 0xFFFF) ^ (k * (17 + j * 2)) ^ key_val | 1))

  def _generate_primes(self, count: int, seed: Optional[bytes] = None) -> List[int]:
    seed_val = sum(seed) if seed else 0
    wheel = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    primes = list(wheel)
    n = 29
    while len(primes) < count:
      is_prime = True
      for p in wheel:
        if n % p == 0:
          is_prime = False
          break
      if is_prime:
        primes.append(n)
      n += 2
    if seed_val:
      for i in range(len(primes)):
        primes[i] = primes[(i + seed_val) % len(primes)]
    return (c_uint32 * len(primes))(*primes[:count])

  def read(self, index: int) -> float:
    return float(self.indices[index]) if index < self.count else 0.0

  def map_data(self, data: bytes) -> List[c_uint32]:
    if not data:
      return (c_uint32 * self.output_size)(*[0] * self.output_size)
    idx0 = data[0] & 0x07
    idx1 = (data[1] & 0x07) if len(data) > 1 else idx0
    return (c_uint32 * self.output_size)(*[self.map_table[i][idx0][idx1] for i in range(self.output_size)])

  def validate(self, data: bytes, expected: List[c_uint32]) -> bool:
    computed = self.map_data(data)
    return all(computed[i] == expected[i] for i in range(min(len(computed), len(expected))))
