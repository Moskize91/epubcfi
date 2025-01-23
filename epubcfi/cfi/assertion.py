from io import StringIO
from .error import TokenizerException


_escaped_chars = ("^", "[", "]", "(", ")", ",", ";", "=")

class _AssertionReader:
  def __init__(self, source: StringIO):
    self._source: StringIO = source
    self._buffer: StringIO = StringIO()
    self._escaped: bool = False

  def read(self) -> str:
    while True:
      char: str = self._source.read(1)
      assertion = self._read(char)
      if assertion is not None:
        return assertion

  def _read(self, char: str) -> str | None:
    if char == "":
      raise TokenizerException("Unexpected EOF")
    if self._escaped:
      if char not in _escaped_chars:
        raise TokenizerException(f"Unexpected character after escaped symbol: {char}")
      self._buffer.write(char)
      self._escaped = False
    elif char == "^":
      self._escaped = True
    elif char == "]":
      text = self._buffer.getvalue()
      if text == "":
        raise TokenizerException("Empty assertion is not allowed")
      return text
    else:
      self._buffer.write(char)
    return None

def read_assertion(source: StringIO) -> str:
  return _AssertionReader(source).read()

def str_assertion(assertion: str | None) -> str:
  if assertion is None:
    return ""
  buffer = StringIO()
  buffer.write("[")
  for char in assertion:
    if char in _escaped_chars:
      buffer.write("^")
    buffer.write(char)
  buffer.write("]")
  return buffer.getvalue()
