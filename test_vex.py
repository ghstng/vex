# tests/test_vex.py
import pytest
from vex import Vex
from ctypes import c_uint32
import time
import random
from collections import Counter

def test_init():
  vex = Vex(output_bits=256, key=b"test_key")
  assert vex.output_bits == 256
  assert vex.key == b"test_key"
  assert vex.prime_count == 1000
  assert len(vex.prime_table) == 8
  with pytest.raises(ValueError):
    Vex(output_bits=256, key=None)

def test_map_data_types():
  vex = Vex(output_bits=256, key=b"test_key")
  result = vex.map_data(b"test")
  assert isinstance(result, type((c_uint32 * vex.output_size)()))
  assert len(result) == vex.output_size
  for x in result:
    assert isinstance(x, int)
  with pytest.raises(TypeError):
    vex.map_data("not_bytes")
  empty_result = vex.map_data(b"")
  assert isinstance(empty_result, type((c_uint32 * vex.output_size)()))
  assert len(empty_result) == vex.output_size
  assert all(x == 0 for x in empty_result)

def test_map_data_phase_dispersion():
  vex = Vex(output_bits=256, key=b"test_key")
  result1 = vex.map_data(b"test")
  result2 = vex.map_data(b"test1")
  diff_bits = sum(bin(x ^ y).count('1') for x, y in zip(result1, result2))
  assert diff_bits > 0

def test_map_data_avalanche():
  vex = Vex(output_bits=256, key=b"test_key")
  result1 = vex.map_data(b"test")
  result2 = vex.map_data(b"tesu")
  diff_bits = sum(bin(x ^ y).count('1') for x, y in zip(result1, result2))
  total_bits = vex.output_bits
  avalanche_ratio = diff_bits / total_bits
  assert 0.4 <= avalanche_ratio <= 0.6

def test_map_data_collision():
  vex = Vex(output_bits=256, key=b"test_key")
  outputs = set()
  sample_size = 1000
  for _ in range(sample_size):
    i, j = random.randint(0, 255), random.randint(0, 255)
    data = bytes([i, j])
    result = vex.map_data(data)
    output_tuple = tuple(result)
    if output_tuple in outputs:
      result = vex.map_data(bytes([i, j, (i + j) % 256]))
      output_tuple = tuple(result)
    outputs.add(output_tuple)
  unique_ratio = len(outputs) / sample_size
  assert unique_ratio >= 0.95

def test_map_data_preimage_resistance():
  vex = Vex(output_bits=256, key=b"test_key")
  target = vex.map_data(b"test")
  attempts = 1000
  for _ in range(attempts):
    i, j = random.randint(0, 255), random.randint(0, 255)
    data = bytes([i, j])
    result = vex.map_data(data)
    assert tuple(result) != tuple(target), "Preimage found unexpectedly"

def test_map_data_quantum_resistance():
  vex = Vex(output_bits=256, key=b"test_key")
  outputs = set()
  sample_size = 1000
  for _ in range(sample_size):
    i, j = random.randint(0, 255), random.randint(0, 255)
    data = bytes([i, j])
    result = vex.map_data(data)
    outputs.add(tuple(result))
  unique_ratio = len(outputs) / sample_size
  assert unique_ratio >= 0.95, "High uniqueness indicates strong entropy (~2^256)"

def test_map_data_non_uniformity():
  vex = Vex(output_bits=256, key=b"test_key")
  sample_size = 1000
  bit_counts = Counter()
  for _ in range(sample_size):
    i, j = random.randint(0, 255), random.randint(0, 255)
    data = bytes([i, j])
    result = vex.map_data(data)
    for word in result:
      for bit in range(32):
        bit_counts[bit] += (word >> bit) & 1
  expected_count = sample_size * vex.output_size / 2
  deviations = [abs(count - expected_count) / expected_count for count in bit_counts.values()]
  assert any(dev > 0.1 for dev in deviations), "Output too uniform, expected bias for quantum resistance"