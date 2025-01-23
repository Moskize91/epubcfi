import os
import unittest

from epubcfi.cfi import parse
from epubcfi.epub import EpubNode

CONTEXT = os.path.dirname(os.path.abspath(__file__))

class TestEPub(unittest.TestCase):

  def test_pick_ncx_label_from_file(self):
    epub_file = os.path.join(CONTEXT, "assets", "zip_sample.epub")
    with EpubNode(remove_cache_path=True) as epub:
      cfi_path = parse("sample.epub#epubcfi(/6/16!:32)")
      label = epub.ncx_label(epub_file, cfi_path)
      self.assertEqual(label, "Introduction")
