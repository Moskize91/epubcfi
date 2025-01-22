# https://idpf.org/epub/linking/cfi/epub-cfi.html#sec-sorting

from io import StringIO
from dataclasses import dataclass
from functools import total_ordering
from typing import Self

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
  
  def __lt__(self, obj: Self) -> bool:
    return False

  def __gt__(self, obj: Self) -> bool:
    return False

  def __le__(self, obj: Self) -> bool:
    return isinstance(obj, Redirect)

  def __ge__(self, obj: Self) -> bool:
    return isinstance(obj, Redirect)

  def __eq__(self, obj: Self) -> bool:
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
  
  def __lt__(self, obj: Self) -> bool:
    if not isinstance(obj, PathRange):
      return True
    step1, step2 = self._skip_common_steps_head(obj)
    if step1 and step2:
      return step1 < step2
    elif step1:
      return True
    elif step2:
      return False
    else:
      offset1, offset2 = self._convert_offset_to_comparable_pairs(obj)
      return offset1 < offset2

  def __gt__(self, obj: Self) -> bool:
    if not isinstance(obj, PathRange):
      return False
    step1, step2 = self._skip_common_steps_head(obj)
    if step1 and step2:
      return step1.index > step2.index
    elif step1:
      return False
    elif step2:
      return True
    else:
      offset1, offset2 = self._convert_offset_to_comparable_pairs(obj)
      return offset1 > offset2

  def __le__(self, obj: Self) -> bool:
    if not isinstance(obj, PathRange):
      return True
    step1, step2 = self._skip_common_steps_head(obj)
    if step1 and step2:
      return step1.index <= step2.index
    elif step1:
      return True
    elif step2:
      return False
    else:
      offset1, offset2 = self._convert_offset_to_comparable_pairs(obj)
      return offset1 <= offset2

  def __ge__(self, obj: Self) -> bool:
    if not isinstance(obj, PathRange):
      return False
    step1, step2 = self._skip_common_steps_head(obj)
    if step1 and step2:
      return step1.index >= step2.index
    elif step1:
      return False
    elif step2:
      return True
    else:
      offset1, offset2 = self._convert_offset_to_comparable_pairs(obj)
      return offset1 >= offset2

  def __eq__(self, obj: Self) -> bool:
    if not isinstance(obj, PathRange):
      return False
    step1, step2 = self._skip_common_steps_head(obj)
    if step1 or step2:
      return False
    offset1, offset2 = self._convert_offset_to_comparable_pairs(obj)
    return offset1 == offset2
  
  def _skip_common_steps_head(self, obj: Self):
    index = 0
    for s1, s2 in zip(self.steps, obj.steps):
      if s1 != s2:
        break
      index += 1
    step1: Redirect | Step | None = None
    step2: Redirect | Step | None = None
    if index < len(self.steps):
      step1 = self.steps[index]
    if index < len(obj.steps):
      step2 = obj.steps[index]
    return step1, step2
  
  def _convert_offset_to_comparable_pairs(self, obj: Self):
    offset1 = self.offset
    offset2 = obj.offset
    type1 = self._offset_type_id(offset1)
    type2 = self._offset_type_id(offset2)

    if type1 < type2:
      return (0, 1)
    elif type1 > type2:
      return (1, 0)
    else:
      return (offset1, offset2)

  def _offset_type_id(self, offset: Offset | None):
    if offset is None:
      return 0
    elif isinstance(offset, CharacterOffset):
      return 1
    elif isinstance(offset, TemporalOffset):
      return 2
    elif isinstance(offset, TemporalSpatialOffset):
      return 3
    elif isinstance(offset, SpatialOffset):
      return 4
    else:
      raise ValueError(f"Unknown offset type: {offset}")
  
@dataclass
@total_ordering
class PathRange:
  parent: Path
  start: Path
  end: Path

  def __str__(self):
    return f"{self.parent},{self.start},{self.end}"
  
  def __lt__(self, obj: Self) -> bool:
    if not isinstance(obj, PathRange):
      return True
    if self.parent != obj.parent:
      return self.parent < obj.parent
    elif self.start != obj.start:
      return self.start < obj.start
    else:
      return self.end < obj.end

  def __gt__(self, obj: Self) -> bool:
    if not isinstance(obj, PathRange):
      return False
    if self.parent != obj.parent:
      return self.parent > obj.parent
    elif self.start != obj.start:
      return self.start > obj.start
    else:
      return self.end > obj.end

  def __le__(self, obj: Self) -> bool:
    if not isinstance(obj, PathRange):
      return True
    if self.parent != obj.parent:
      return self.parent <= obj.parent
    elif self.start != obj.start:
      return self.start <= obj.start
    else:
      return self.end <= obj.end

  def __ge__(self, obj: Self) -> bool:
    if not isinstance(obj, PathRange):
      return False
    if self.parent != obj.parent:
      return self.parent >= obj.parent
    elif self.start != obj.start:
      return self.start >= obj.start
    else:
      return self.end >= obj.end

  def __eq__(self, obj: Self) -> bool:
    if not isinstance(obj, PathRange):
      return False
    return (
      self.parent == obj.parent and \
      self.start == obj.start and \
      self.end == obj.end
    )

ParsedPath = Path | PathRange