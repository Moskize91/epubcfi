import unittest

from src.epubcfi.path import PathRange
from src.epubcfi.cfi import split, to_absolute, _capture_cfi

class TestCFI(unittest.TestCase):

  def test_to_absolute(self):
    prefix, results = split("book.epub#epubcfi(/6/4,!/2[foobar],/10/4[foz])")
    self.assertTrue(isinstance(results, PathRange))
    start, end = to_absolute(results)
    self.assertEqual(prefix, "book.epub")
    self.assertEqual(str(start), "/6/4!/2[foobar]")
    self.assertEqual(str(end), "/6/4/10/4[foz]")

  def test_format(self):
    prefix, results = split("book.epub#epubcfi(/6/4,!/2[foobar],/10/4[foz])")
    self.assertTrue(isinstance(results, PathRange))
    self.assertEqual(prefix, "book.epub")
    self.assertEqual(str(results), "/6/4,!/2[foobar],/10/4[foz]")

  def test_capture_cfi(self):
    pairs = [(
      "book.epub#epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/3:10)",
      "/6/4[chap01ref]!/4[body01]/10[para05]/3:10",
    ), (
      "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/3:10)",
      "/6/4[chap01ref]!/4[body01]/10[para05]/3:10",
    ), (
      "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/3:10)foobar",
      None,
    )]
    for source, target in pairs:
      _, cfi = _capture_cfi(source)
      self.assertEqual(cfi, target)