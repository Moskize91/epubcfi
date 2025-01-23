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
@total_ordering
class CharacterOffset(Offset):
  value: int

  def __str__(self) -> str:
    assertion = str_assertion(self.assertion)
    return f":{self.value}{assertion}"

  def __lt__(self, obj: Any) -> bool:
    if not isinstance(obj, CharacterOffset):
      return False
    return self.value < obj.value

  def __gt__(self, obj: Any) -> bool:
    if not isinstance(obj, CharacterOffset):
      return True
    return self.value > obj.value

  def __le__(self, obj: Any) -> bool:
    if not isinstance(obj, CharacterOffset):
      return False
    return self.value <= obj.value

  def __ge__(self, obj: Any) -> bool:
    if not isinstance(obj, CharacterOffset):
      return True
    return self.value >= obj.value

  def __eq__(self, obj: Any) -> bool:
    if not isinstance(obj, CharacterOffset):
      return False
    return self.value == obj.value

# https://idpf.org/epub/linking/cfi/epub-cfi.html#sec-path-terminating-temporal
@dataclass
@total_ordering
class TemporalOffset(Offset):
  seconds: int

  def __str__(self) -> str:
    assertion = str_assertion(self.assertion)
    return f"~{self.seconds}{assertion}"

  def __lt__(self, obj: Any) -> bool:
    if not isinstance(obj, TemporalOffset):
      return False
    return self.seconds < obj.seconds

  def __gt__(self, obj: Any) -> bool:
    if not isinstance(obj, TemporalOffset):
      return True
    return self.seconds > obj.seconds

  def __le__(self, obj: Any) -> bool:
    if not isinstance(obj, TemporalOffset):
      return False
    return self.seconds <= obj.seconds

  def __ge__(self, obj: Any) -> bool:
    if not isinstance(obj, TemporalOffset):
      return True
    return self.seconds >= obj.seconds

  def __eq__(self, obj: Any) -> bool:
    if not isinstance(obj, TemporalOffset):
      return False
    return self.seconds == obj.seconds

# https://idpf.org/epub/linking/cfi/epub-cfi.html#sec-path-terminating-spatial
@dataclass
@total_ordering
class SpatialOffset(Offset):
  x: int
  y: int

  def __str__(self) -> str:
    assertion = str_assertion(self.assertion)
    return f"@{self.x}:{self.y}{assertion}"

  def __lt__(self, obj: Any) -> bool:
    if not isinstance(obj, SpatialOffset):
      return False
    return (self.y, self.x) < (obj.y, obj.x)

  def __gt__(self, obj: Any) -> bool:
    if not isinstance(obj, SpatialOffset):
      return True
    return (self.y, self.x) > (obj.y, obj.x)

  def __le__(self, obj: Any) -> bool:
    if not isinstance(obj, SpatialOffset):
      return False
    return (self.y, self.x) <= (obj.y, obj.x)

  def __ge__(self, obj: Any) -> bool:
    if not isinstance(obj, SpatialOffset):
      return True
    return (self.y, self.x) >= (obj.y, obj.x)

  def __eq__(self, obj: Any) -> bool:
    if not isinstance(obj, SpatialOffset):
      return False
    return (self.y, self.x) == (obj.y, obj.x)

# https://idpf.org/epub/linking/cfi/epub-cfi.html#sec-path-terminating-tempspatial
@dataclass
@total_ordering
class TemporalSpatialOffset(TemporalOffset):
  x: int
  y: int

  def __str__(self) -> str:
    assertion = str_assertion(self.assertion)
    return f"~{self.seconds}@{self.x}:{self.y}{assertion}"

  def __lt__(self, obj: Any) -> bool:
    if not isinstance(obj, TemporalSpatialOffset):
      return False
    return (self.seconds, self.y, self.x) < (obj.seconds, obj.y, obj.x)

  def __gt__(self, obj: Any) -> bool:
    if not isinstance(obj, TemporalSpatialOffset):
      return True
    return (self.seconds, self.y, self.x) > (obj.seconds, obj.y, obj.x)

  def __le__(self, obj: Any) -> bool:
    if not isinstance(obj, TemporalSpatialOffset):
      return False
    return (self.seconds, self.y, self.x) <= (obj.seconds, obj.y, obj.x)

  def __ge__(self, obj: Any) -> bool:
    if not isinstance(obj, TemporalSpatialOffset):
      return True
    return (self.seconds, self.y, self.x) >= (obj.seconds, obj.y, obj.x)

  def __eq__(self, obj: Any) -> bool:
    if not isinstance(obj, TemporalSpatialOffset):
      return False
    return (self.seconds, self.y, self.x) == (obj.seconds, obj.y, obj.x)
