import unittest

from epubcfi.path import PathRange
from epubcfi.parser import parse


class TestParser(unittest.TestCase):

  def test_parse_cfi(self):
    cfi_list = [
      "/6/4[chap01ref]!/4[body01]/10[para05]/3:10",
      "/6/4[chap^]01^^ref]!/4[body^[01]/10[para05]/3:10",
      "/6/4[chap01ref]@20:100",
      "/6/4[chap01ref]~2048",
      "/6/4[chap01ref]~2042@20:100",
    ]
    for cfi in cfi_list:
      path = parse(cfi)
      self.assertEqual(cfi, str(path))

  def test_simple_range(self):
    cfi_list = [
      "/6/4!/2[foobar],/10/4[foobar],/10",
      "/6/4!/2[foobar],!/10/4[foobar]:23,!/10",
      "/6/4!/2[foobar],!:12,!/10",
    ]
    for cfi in cfi_list:
      result = parse(cfi)
      self.assertTrue(isinstance(result, PathRange))
      self.assertEqual(cfi, str(result))
