# vex.py
from ctypes import c_uint32
from typing import List, Optional

class Vex:
  def __init__(self, output_bits: int = 256, key: Optional[bytes] = b"default_key"):
    if key is None:
      raise ValueError("Key is mandatory")
    self.output_bits = max(64, min(output_bits, 256))
    self.key = key
    self.prime_count = 1000
    self.output_size = max(2, self.output_bits // 32)
    table_size = 8
    self.prime_table = ((c_uint32 * table_size * table_size) * self.output_size)()
    key_val = sum(key)
    indices = self._generate_primes()
    for j in range(self.output_size):
      for i in range(table_size):
        for k in range(table_size):
          self.prime_table[j][i][k] = c_uint32((indices[i % self.prime_count] ^ ((indices[(k + j + 1) % self.prime_count] ^ (i << (7 + j)) ^ (k >> (2 + j)) ^ (indices[i % self.prime_count] & 65535) ^ (k * (17 + j * 2))) ^ key_val)) | 1)

  def _generate_primes(self) -> List[int]:
    wheel = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    primes = list(wheel)
    n = 29
    while len(primes) < self.prime_count:
      is_prime = True
      for p in wheel:
        if n % p == 0:
          is_prime = False
          break
      if is_prime:
        primes.append(n)
      n += 2
    return (c_uint32 * len(primes))(*primes[:self.prime_count])

  def map_data(self, data: bytes) -> c_uint32:
    if not isinstance(data, bytes):
      raise TypeError("Data must be bytes")
    if not data:
      return (c_uint32 * self.output_size)(*([0] * self.output_size))
    table_size = 8
    idx0 = data[0] % table_size
    idx1 = (data[1] % table_size) if len(data) > 1 else idx0
    result = (c_uint32 * self.output_size)()
    for i in range(self.output_size):
      result[i] = self.prime_table[i][idx0][idx1]
    return result