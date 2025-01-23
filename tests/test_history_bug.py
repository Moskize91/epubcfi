import unittest

from epubcfi.cfi import parse, _capture_cfi

class TestHistoryBug(unittest.TestCase):

  def test_parse_and_compare(self):
    history_expressions = [
      "epubcfi(/6/24[id18]!/4/422/2/3,:227,:228)",
      "epubcfi(/6/22[id17]!/4/62/1,:0,:59)"
    ]
    for expression in history_expressions:
      _, cfi = _capture_cfi(expression)
      path = parse(expression)
      self.assertEqual(cfi, str(path))
