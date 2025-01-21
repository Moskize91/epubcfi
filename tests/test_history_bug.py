import unittest
from src.epubcfi.cfi import split, format, _capture_cfi

class TestHistoryBug(unittest.TestCase):

  def test_parse_and_compare(self):
    history_expressions = [
      "epubcfi(/6/24[id18]!/4/422/2/3,:227,:228)",
    ]
    for expression in history_expressions:
      _, path = split(expression)
      _, cfi = _capture_cfi(expression)
      self.assertEqual(cfi, format(path))