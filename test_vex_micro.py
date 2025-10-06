# tests/test_vex_micro.py
import pytest
from vex import Vex
from ctypes import c_uint32

def test_map_data_type_output():
  vex = Vex(output_bits=256, key=b"test_key")
  result = vex.map_data(b"test")
  assert isinstance(result, type((c_uint32 * vex.output_size)()))
  assert len(result) == vex.output_size
  for x in result:
    assert isinstance(x, int)  # Elements are int values from c_uint32 array

def test_map_data_empty():
  vex = Vex(output_bits=256, key=b"test_key")
  result = vex.map_data(b"")
  assert isinstance(result, type((c_uint32 * vex.output_size)()))
  assert len(result) == vex.output_size
  assert all(x == 0 for x in result)

def test_map_data_invalid_input():
  vex = Vex(output_bits=256, key=b"test_key")
  with pytest.raises(TypeError):
    vex.map_data("not_bytes")