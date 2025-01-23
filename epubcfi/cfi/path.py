# https://idpf.org/epub/linking/cfi/epub-cfi.html#sec-sorting

from __future__ import annotations
from io import StringIO
from dataclasses import dataclass
from functools import total_ordering
from typing import Any
from .tokenizer import (
  Step,
  CharacterOffset,
  TemporalOffset,
  SpatialOffset,
  TemporalSpatialOffset,
)

Offset = CharacterOffset | TemporalOffset | SpatialOffset | TemporalSpatialOffset

@dataclass
@total_ordering
class Redirect:
  def __str__(self) -> str:
    return "!"

  def __lt__(self, _: Any) -> bool:
    return False

  def __gt__(self, _: Any) -> bool:
    return False

  def __le__(self, obj: Any) -> bool:
    return isinstance(obj, Redirect)

  def __ge__(self, obj: Any) -> bool:
    return isinstance(obj, Redirect)

  def __eq__(self, obj: Any) -> bool:
    return isinstance(obj, Redirect)

@dataclass
@total_ordering
class Path:
  steps: list[Redirect | Step]
  offset: Offset | None

  def start_with_redirect(self) -> bool:
    return isinstance(self.steps[0], Redirect)

  def __str__(self):
    buffer = StringIO()
    for step in self.steps:
      buffer.write(str(step))
    if self.offset is not None:
      buffer.write(str(self.offset))
    return buffer.getvalue()

  def __lt__(self, obj: Any) -> bool:
    if not isinstance(obj, ParsedPath):
      return True
    tail1, tail2 = self._skip_common_steps_head(obj)
    return tail1 < tail2

  def __gt__(self, obj: Any) -> bool:
    if not isinstance(obj, ParsedPath):
      return False
    tail1, tail2 = self._skip_common_steps_head(obj)
    return tail1 > tail2

  def __le__(self, obj: Any) -> bool:
    if not isinstance(obj, ParsedPath):
      return True
    tail1, tail2 = self._skip_common_steps_head(obj)
    return tail1 <= tail2

  def __ge__(self, obj: Any) -> bool:
    if not isinstance(obj, ParsedPath):
      return False
    tail1, tail2 = self._skip_common_steps_head(obj)
    return tail1 >= tail2

  def __eq__(self, obj: Any) -> bool:
    if not isinstance(obj, ParsedPath):
      return False
    tail1, tail2 = self._skip_common_steps_head(obj)
    return tail1 == tail2

  def _skip_common_steps_head(self, obj: ParsedPath):
    obj_steps: list[Redirect | Step]
    obj_offset: Offset | None
    index: int = 0

    if isinstance(obj, PathRange):
      obj_steps = obj.parent.steps + obj.start.steps
      obj_offset = obj.start.offset
    else:
      obj_steps = obj.steps
      obj_offset = obj.offset

    for s1, s2 in zip(self.steps, obj_steps):
      if s1 != s2:
        break
      index += 1

    tail1: Redirect | Step | Offset | None = None
    tail2: Redirect | Step | Offset | None = None

    if index < len(self.steps):
      tail1 = self.steps[index]
    else:
      tail1 = self.offset
    if index < len(obj_steps):
      tail2 = obj_steps[index]
    else:
      tail2 = obj_offset

    type1 = self._offset_type_id(tail1)
    type2 = self._offset_type_id(tail2)

    if type1 < type2:
      return (0, 1)
    elif type1 > type2:
      return (1, 0)
    else:
      return (tail1, tail2)

  def _offset_type_id(self, tail: Redirect | Step | Offset | None):
    # https://idpf.org/epub/linking/cfi/epub-cfi.html#sec-sorting
    # different step types come in the following order from least important to most important:
    # character offset (:), child (/), temporal-spatial (~ or @), reference/indirect (!).
    if tail is None:
      return 0
    elif isinstance(tail, Redirect):
      return 1
    elif isinstance(tail, SpatialOffset):
      return 2
    elif isinstance(tail, TemporalOffset):
      return 3
    elif isinstance(tail, TemporalSpatialOffset):
      return 4
    elif isinstance(tail, Step):
      return 5
    elif isinstance(tail, CharacterOffset):
      return 6
    else:
      raise ValueError(f"Unknown offset type: {tail}")

@dataclass
@total_ordering
class PathRange:
  parent: Path
  start: Path
  end: Path

  def __str__(self):
    return f"{self.parent},{self.start},{self.end}"

  def __lt__(self, obj: Any) -> bool:
    if not isinstance(obj, ParsedPath):
      return True
    if isinstance(obj, Path):
      return obj > self
    return self._to_tuple() < obj._to_tuple()

  def __gt__(self, obj: Any) -> bool:
    if not isinstance(obj, ParsedPath):
      return False
    if isinstance(obj, Path):
      return obj < self
    return self._to_tuple() > obj._to_tuple()

  def __le__(self, obj: Any) -> bool:
    if not isinstance(obj, ParsedPath):
      return True
    if isinstance(obj, Path):
      return obj >= self
    return self._to_tuple() <= obj._to_tuple()

  def __ge__(self, obj: Any) -> bool:
    if not isinstance(obj, ParsedPath):
      return False
    if isinstance(obj, Path):
      return obj <= self
    return self._to_tuple() >= obj._to_tuple()

  def __eq__(self, obj: Any) -> bool:
    if not isinstance(obj, ParsedPath):
      return False
    if isinstance(obj, Path):
      return obj == self
    return self._to_tuple() == obj._to_tuple()

  def _to_tuple(self):
    return (self.parent, self.start, self.end)

  def _obj_to_tuple(self, obj: ParsedPath):
    if isinstance(obj, PathRange):
      return (obj.parent, obj.start, obj.end)
    else:
      return obj, obj, obj

ParsedPath = Path | PathRange
