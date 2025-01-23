import os
import unittest

from epubcfi.cfi import Step
from epubcfi.epub.picker import Picker

CONTEXT = os.path.dirname(os.path.abspath(__file__))

class TestPicker(unittest.TestCase):

  def test_basic_cursor_forwarding(self):
    picker = Picker(os.path.join(CONTEXT, "assets", "sample.epub"))
    cursor = picker.cursor()
    cursor.forward(Step(
      index=1,
      assertion=None,
    ))
