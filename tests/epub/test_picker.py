import os
import unittest

from epubcfi.cfi import parse
from epubcfi.epub.picker import pick
from epubcfi.epub.ncx_finder import find_ncx_label

CONTEXT = os.path.dirname(os.path.abspath(__file__))

class TestPicker(unittest.TestCase):

  def test_pick_from_book(self):
    book = pick(os.path.join(CONTEXT, "assets", "sample.epub"))
    self.assertEqual(book.title, "The Sublime Object of Ideology")
    self.assertEqual(book.authors, ["Slavoj Žižek"])
    self.assertListEqual(book.ncx, [
      ("Cover Page", "./CoverJohnBrownvl3063thmfuwrmefxonbsyetochqcom.xhtml"),
      ("Title Page", "./02_TitleJohnBrownvlthmfuwrmefxonbsyetoc4345hqcom.xhtml"),
      ("Copyright Page", "./03_CopyrightJohnBrownv1470lthmfuwrmefxonbsyetochqcom.xhtml"),
      ("Contents", "./04_ContentsJohnBrownvlthmfuwrmefxonbsyetochq7136com.xhtml"),
      ("Preface to the New Edition: The Idea’s Constipation", "./05_PrefaceJohnBrownvlthmfuwr7033mefxonbsyetochqcom.xhtml"),
      ("Introduction", "./06_IntroJohnBrownvlthmfuwrmefxonbsye19tochqcom.xhtml"),
      ("I. The Symptom", "./07_Part01JohnBrownvlthmfuwrmefxo6686nbsyetochqcom.xhtml"),
      ("1. How Did Marx Invent the Symptom?", "./08_Chap01JohnBrownvlthmfuwrmefxonbsyetoch4544qcom.xhtml"),
      ("2. From Symptom to Sinthome", "./09_Chap02JohnBrownv1142lthmfuwrmefxonbsyetochqcom.xhtml"),
      ("II. Lack in the Other", "./10_Part02JohnBr5372ownvlthmfuwrmefxonbsyetochqcom.xhtml"),
      ("3. ‘Che Vuoi?’", "./11_Chap03JohnBrownv5026lthmfuwrmefxonbsyetochqcom.xhtml"),
      ("4. You Only Die Twice", "./12_Chap04JohnBrownvlthmfuwrmefxonbsye3980tochqcom.xhtml"),
      ("III. The Subject", "./13_Part03JohnBrownvlthmfuwrmefxonbsy5496etochqcom.xhtml"),
      ("5. Which Subject of the Real?", "./14_Chap05JohnBrownvlth8466mfuwrmefxonbsyetochqcom.xhtml"),
      ("6. ‘Not Only as Substance, but Also as Subject’", "./15_Chap06JohnBrow5325nvlthmfuwrmefxonbsyetochqcom.xhtml"),
      ("Notes", "./16_NotesJohnBrownvlthmfuwrmefx8621onbsyetochqcom.xhtml"),
      ("Index", "./17_IndexJohnBrownvlthmfuwrme7338fxonbsyetochqcom.xhtml"),
      ("This eBook is licensed to John Brown, vlthmfuwrmefxonbsy@etochq.com on 10/22/2020", "./disclaimerJohnBrown5019vlthmfuwrmefxonbsyetochqcom.xhtml")
    ])

  def test_find_label(self):
    book = pick(os.path.join(CONTEXT, "assets", "sample.epub"))
    except_labels = [
      ("sample.epub#epubcfi(/6/16!:32)", "Introduction"),
      ("sample.epub#epubcfi(/6/24!)", "II. Lack in the Other"),
      ("sample.epub#epubcfi(/4/34!)", "III. The Subject"),
    ]
    with open(book.content_path, "rb") as reader:
      for cfi, expected_label in except_labels:
        path = parse(cfi)
        label = find_ncx_label(book, reader, path)
        self.assertEqual(label, expected_label)
        reader.seek(0)
