# tests/test_vex.py
import pytest
from vex import Vex
from ctypes import c_uint32
import time

def test_init():
  vex = Vex(output_bits=256, key=b"test_key")
  assert vex.output_bits == 256
  assert vex.key == b"test_key"
  assert vex.prime_count == 1000
  assert len(vex.prime_table) == 8  # output_size = 256 // 32
  with pytest.raises(ValueError):
    Vex(output_bits=256, key=None)

def test_map_data_types():
  vex = Vex(output_bits=256, key=b"test_key")
  result = vex.map_data(b"test")
  assert isinstance(result, type((c_uint32 * vex.output_size)()))
  assert len(result) == vex.output_size
  for x in result:
    assert isinstance(x, int)  # Elements are int values from c_uint32 array
  with pytest.raises(TypeError):
    vex.map_data("not_bytes")
  empty_result = vex.map_data(b"")
  assert isinstance(empty_result, type((c_uint32 * vex.output_size)()))
  assert len(empty_result) == vex.output_size
  assert all(x == 0 for x in empty_result)