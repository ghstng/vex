# tests/test_vex.py
def test_map_data_collision_resistance():
  vex = Vex(buffer_size=100, prime_base=2, nesting_depth=8, output_bits=256, prime_count=200)
  seen = set()
  for i in range(256):
    for j in range(256):
      data = bytes([i, j])
      result = vex.map_data(data)
      hash_val = tuple(result)  # Convert list to tuple for hashing
      assert hash_val not in seen, f"Collision at inputs {i}, {j}"
      seen.add(hash_val)
  assert len(seen) >= 256 * 256 * 0.95  # ~95% unique outputs

def test_map_data_preimage_resistance():
  vex = Vex(buffer_size=100, prime_base=2, nesting_depth=8, output_bits=256, prime_count=200, key=b"secret")
  data = b"\x42\x01"
  target = vex.map_data(data)
  for i in range(256):
    for j in range(256):
      test_data = bytes([i, j])
      if test_data != data:
        assert vex.map_data(test_data) != target, f"Preimage found at {i}, {j}"

def test_map_data_avalanche():
  vex = Vex(buffer_size=100, prime_base=2, nesting_depth=8, output_bits=256, prime_count=200)
  data1 = b"\x42\x01"
  data2 = b"\x43\x01"
  hash1 = vex.map_data(data1)
  hash2 = vex.map_data(data2)
  bit_flips = sum(bin(h1.value ^ h2.value).count('1') for h1, h2 in zip(hash1, hash2))
  total_bits = 32 * len(hash1)
  flip_rate = bit_flips / total_bits
  assert flip_rate >= 0.4, f"Avalanche effect weak: {flip_rate:.2f}, expected >= 0.4"

def test_map_data_performance():
  vex = Vex(buffer_size=100, prime_base=2, nesting_depth=8, output_bits=256, prime_count=200)
  data = b"\x42\x01" * 500
  start = time.perf_counter()
  for _ in range(1000):
    vex.map_data(data)
  elapsed = (time.perf_counter() - start) * 1e6 / 1000
  assert elapsed <= 22, f"map_data too slow: {elapsed:.2f} µs, expected <= 22 µs"
