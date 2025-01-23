import unittest

from epubcfi.path import PathRange
from epubcfi.cfi import parse, split, to_absolute, _capture_cfi


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

  def test_sorted_cfi(self):
    expressions = [
      "book.epub#epubcfi(/6/4/321)",
      "book.epub#epubcfi(/6/4)",
      "book.epub#epubcfi(/6/4/123)",
      "book.epub#epubcfi(/6/4@0:99)",
      "book.epub#epubcfi(/6/4@100:33)",
      "book.epub#epubcfi(/6/4:23)",
    ]
    cfi_list = [parse(e) for e in expressions]
    cfi_list = [cfi for cfi in cfi_list if cfi is not None]
    cfi_list.sort()
    self.assertEqual([str(cfi) for cfi in cfi_list], [
      "/6/4",
      "/6/4@100:33",
      "/6/4@0:99",
      "/6/4/123",
      "/6/4/321",
      "/6/4:23",
    ])
