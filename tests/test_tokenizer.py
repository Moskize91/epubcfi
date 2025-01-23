import unittest

from epubcfi.tokenizer import Token, EOF, Tokenizer


class TestTokenizer(unittest.TestCase):

  def test_tokenizer(self):
    cfi_list = [
      "/6/4[chap01ref]!/4[body01]/10[para05]/3:10",
      "/6/4[chap^]01^^ref]!/4[body^[01]/10[para05]/3:10",
      "/6/4[chap01ref]@20:100",
      "/6/4[chap01ref]~2048",
      "/6/4[chap01ref]~2042@20:100",
    ]
    for cfi in cfi_list:
      token: Token
      tokens: list[Token] = []
      tokenizer = Tokenizer(cfi)

      while True:
        token = tokenizer.read()
        if isinstance(token, EOF):
          break
        tokens.append(token)

      self.assertEqual(cfi, "".join(map(str, tokens)))
