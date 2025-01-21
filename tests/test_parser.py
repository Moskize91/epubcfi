import unittest
from src.epubcfi.parser import _capture_cfi

class TestChunk(unittest.TestCase):

  def test_capture_cfi(self):
    self.assertEqual(
      _capture_cfi("book.epub#epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/3:10)"),
      "/6/4[chap01ref]!/4[body01]/10[para05]/3:10",
    )
    self.assertEqual(
      _capture_cfi("epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/3:10)"),
      "/6/4[chap01ref]!/4[body01]/10[para05]/3:10",
    )
    self.assertEqual(
      _capture_cfi("epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/3:10)foobar"),
      None,
    )