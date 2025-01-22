from dataclasses import dataclass
from functools import total_ordering
from typing import Any, Literal
from .assertion import str_assertion

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

# https://idpf.org/epub/linking/cfi/epub-cfi.html#sec-sorting
@dataclass
@total_ordering
class Step(Token):
  index: int
  assertion: str | None

  def __str__(self) -> str:
    assertion = str_assertion(self.assertion)
    return f"/{self.index}{assertion}"

  def __lt__(self, obj: Any) -> bool:
    if not isinstance(obj, Step):
      return False
    return self.index < obj.index

  def __gt__(self, obj: Any) -> bool:
    if not isinstance(obj, Step):
      return True
    return self.index > obj.index

  def __le__(self, obj: Any) -> bool:
    if not isinstance(obj, Step):
      return False
    return self.index <= obj.index

  def __ge__(self, obj: Any) -> bool:
    if not isinstance(obj, Step):
      return True
    return self.index >= obj.index

  def __eq__(self, obj: Any) -> bool:
    if not isinstance(obj, Step):
      return False
    return self.index == obj.index

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
  