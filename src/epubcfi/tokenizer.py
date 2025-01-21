from enum import Enum
from io import StringIO
from dataclasses import dataclass
from typing import Literal
from .assertion import read_assertion, str_assertion
from .error import TokenizerException

class Phase(Enum):
  Ready = 1
  Step = 2
  Offset = 3

@dataclass
class Token:
  def __str__(self) -> str:
    return ""

@dataclass
class EOF(Token):
  pass

@dataclass
class Symbol(Token):
  text: Literal[",", "!"]

  def __str__(self) -> str:
    return self.text

@dataclass
class Step(Token):
  index: int
  assertion: str | None

  def __str__(self) -> str:
    assertion = str_assertion(self.assertion)
    return f"/{self.index}{assertion}"

@dataclass
class Offset(Token):
  assertion: str | None

# https://idpf.org/epub/linking/cfi/epub-cfi.html#sec-path-terminating-char
@dataclass
class CharacterOffset(Offset):
  value: int

  def __str__(self) -> str:
    assertion = str_assertion(self.assertion)
    return f":{self.value}{assertion}"

# https://idpf.org/epub/linking/cfi/epub-cfi.html#sec-path-terminating-temporal
@dataclass
class TemporalOffset(Offset):
  seconds: int

  def __str__(self) -> str:
    assertion = str_assertion(self.assertion)
    return f"~{self.seconds}{assertion}"

# https://idpf.org/epub/linking/cfi/epub-cfi.html#sec-path-terminating-spatial
@dataclass
class SpatialOffset(Offset):
  x: int
  y: int

  def __str__(self) -> str:
    assertion = str_assertion(self.assertion)
    return f"@{self.x}:{self.y}{assertion}"

# https://idpf.org/epub/linking/cfi/epub-cfi.html#sec-path-terminating-tempspatial
@dataclass
class TemporalSpatialOffset(TemporalOffset):
  x: int
  y: int

  def __str__(self) -> str:
    assertion = str_assertion(self.assertion)
    return f"~{self.seconds}@{self.x}:{self.y}{assertion}"
  
class Tokenizer:
  def __init__(self, content: str):
    self._phase: Phase = Phase.Ready
    self._inject_char: str = ""
    self._buffer: StringIO = StringIO()
    self._source: StringIO = StringIO(content)
    self._offset_symbol: Literal[":", "@", "~"] = ":"
    self._offset_chain: list[tuple[Literal[":", "@", "~"], int]] = []

  def read(self) -> Token:
    char: str = ""
    while True:
      if self._inject_char == "":
        char = self._source.read(1)
      else:
        char = self._inject_char
        self._inject_char = ""

      token, forward = self._read(char)
      if not forward:
        self._inject_char = char
      if token is not None:
        return token

  def _read(self, char: str) -> tuple[Token | None, bool]:
    if self._phase == Phase.Ready:
      return self._read_when_read(char)
    elif self._phase in (Phase.Step, Phase.Offset):
      return self._read_integer(char)
    else:
      raise Exception(f"Unexpected phase {self._phase}")

  def _read_when_read(self, char: str) -> tuple[Token | None, bool]:
    if char == "":
      return EOF(), True
    elif char in (",", "!"):
      return Symbol(text=char), True
    elif char == "/":
      self._phase = Phase.Step
    elif char in (":", "~", "@"):
      self._offset_symbol = char
      self._phase = Phase.Offset
    else:
      raise TokenizerException(f"Unexpected character: {char}")
    return None, True
    
  def _read_integer(self, char: str) -> tuple[Token | None, bool]:
    if char >= "0" and char <= "9":
      self._buffer.write(char)
      return None, True
    else:
      text: str = self._buffer.getvalue()
      if len(text) > 0 and text.startswith("0"):
        raise TokenizerException(f"{text} leading zero is not allowed")
      integer = int(text)
      self._buffer = StringIO()

      if self._phase == Phase.Step:
        assertion = self._read_assertion_if_need(char)
        step = Step(integer, assertion)
        self._phase = Phase.Ready
        if assertion is None:
          return step, False
        else:
          return step, True

      elif self._phase == Phase.Offset:
        self._offset_chain.append((self._offset_symbol, integer))
        if char in (":", "~", "@"):
          self._offset_symbol = char
          return None, True
        assertion = self._read_assertion_if_need(char)
        offset = self._create_offset(assertion)
        self._phase = Phase.Ready
        return offset, assertion is not None

      else:
        raise Exception(f"Unexpected phase {self._phase}")
      
  def _read_assertion_if_need(self, char: str) -> str | None:
    assertion: str | None = None
    if char == "[":
      assertion = read_assertion(self._source)
    return assertion
      
  def _create_offset(self, assertion: str | None) -> Token:
    token: Token | None = None

    if len(self._offset_chain) == 1:
      symbol, value = self._offset_chain[0]
      if symbol == ":":
        token = CharacterOffset(
          value=value,
          assertion=assertion,
        )
      elif symbol == "~":
        token = TemporalOffset(
          seconds=value,  
          assertion=assertion,
        )
    elif len(self._offset_chain) == 2:
      symbol1, value1 = self._offset_chain[0]
      symbol2, value2 = self._offset_chain[1]
      if symbol1 == "@" and symbol2 == ":":
        token = SpatialOffset(
          x=value1, 
          y=value2,
          assertion=assertion,
        )
    elif len(self._offset_chain) == 3:
      symbol1, value1 = self._offset_chain[0]
      symbol2, value2 = self._offset_chain[1]
      symbol3, value3 = self._offset_chain[2]
      if symbol1 == "~" and symbol2 == "@" and symbol3 == ":":
        token = TemporalSpatialOffset(
          seconds=value1, 
          x=value2, 
          y=value3,
          assertion=assertion,
        )
    if token is None:
      raise TokenizerException(f"Unexpected offset: {self._str_offset_chain()}")
    self._offset_chain.clear()
    return token
      
  def _str_offset_chain(self) -> str:
    buffer = StringIO()
    for symbol, value in self._offset_chain:
      buffer.write(symbol)
      buffer.write(str(value))
    return buffer.getvalue()