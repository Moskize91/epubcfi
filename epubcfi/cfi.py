import re

from .parser import parse as parse_cfi
from .path import Path, PathRange, ParsedPath


def parse(path: str) -> ParsedPath | None:
  _, cfi = _capture_cfi(path)
  if cfi is None:
    return path, None
  return parse_cfi(cfi)

def split(path: str) -> tuple[str, ParsedPath | None]:
  tail, cfi = _capture_cfi(path)
  if cfi is None:
    return path, None
  result = parse_cfi(cfi)
  prefix = path[:len(path) - len(tail)]
  return prefix, result

def to_absolute(r: PathRange) -> tuple[Path, Path]:
  start = Path(
    steps=r.parent.steps + r.start.steps,
    offset=r.start.offset,
  )
  end = Path(
    steps=r.parent.steps + r.end.steps,
    offset=r.end.offset,
  )
  return start, end

def _capture_cfi(path: str):
  matched = re.search(r"(#|^)epubcfi\((.*)\)$", path)
  if matched:
    return matched.group(), matched.group(2)
  else:
    return None, None
