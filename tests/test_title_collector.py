import os
import unittest

from epubcfi.epub.title_collector import _FireCursor

CONTEXT = os.path.dirname(os.path.abspath(__file__))

class TestTitleCollector(unittest.TestCase):

  def test_foo(self):
    file_path = os.path.join(CONTEXT, "epub", "assets", "sample.epub", "09_Chap02JohnBrownv1142lthmfuwrmefxonbsyetochqcom.xhtml")
    result = _FireCursor(file_path, [4, 2, 22]).parse()
    print(result)
