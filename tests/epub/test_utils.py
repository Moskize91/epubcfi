import unittest

from dataclasses import dataclass
from epubcfi.epub.utils import SizeLimitMap


@dataclass
class NeedClose:
  id: int = 0
  did_close: bool = False

  def close(self):
    self.did_close = True

class TestUtils(unittest.TestCase):

  def test_size_limit_map(self):
    limit_map: SizeLimitMap[NeedClose] = SizeLimitMap(
      limit=3,
      on_close=lambda e: e.close(),
    )
    limit_map["1"] = NeedClose(1)
    limit_map["2"] = NeedClose(2)
    limit_map["3"] = NeedClose(3)

    keys: list[str] = []
    values: list[NeedClose] = []

    for key in limit_map.keys():
      keys.append(key)
      values.append(limit_map.get(key))

    self.assertEqual(len(limit_map), 3)
    self.assertEqual(keys, ["1", "2", "3"])
    self.assertEqual(
      [value.id for value in values],
      [1, 2, 3],
    )
    self.assertListEqual(
      [value.did_close for value in values],
      [False, False, False],
    )
    limit_map["4"] = NeedClose(4)
    limit_map["5"] = NeedClose(5)

    for key in limit_map.keys():
      if key > "3":
        keys.append(key)
        values.append(limit_map.get(key))

    self.assertEqual(keys, ["1", "2", "3", "4", "5"])
    self.assertListEqual(
      [value.id for value in values],
      [1, 2, 3, 4, 5],
    )
    self.assertEqual(len(limit_map), 3)
    self.assertEqual(list(limit_map.keys()), ["3", "4", "5"])
    self.assertListEqual(
      [value.did_close for value in values],
      [True, True, False, False, False],
    )

