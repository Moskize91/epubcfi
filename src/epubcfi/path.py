from dataclasses import dataclass
from io import StringIO

from .tokenizer import (
  Step, 
  CharacterOffset,
  TemporalOffset,
  SpatialOffset,
  TemporalSpatialOffset,
)

Offset = CharacterOffset | TemporalOffset | SpatialOffset | TemporalSpatialOffset

@dataclass
class Redirect:
  def __str__(self) -> str:
    return "!"

@dataclass
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
  

PathTuple = tuple[Path, Path, Path]
ParsedPath = Path | PathTuple