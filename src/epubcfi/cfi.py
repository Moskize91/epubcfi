import re

from .parser import parse as parse_cfi
from .path import Path, PathTuple, ParsedPath


def parse(path: str) -> tuple[str, ParsedPath | None]:
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

def format(path: ParsedPath) -> str:
  if isinstance(path, Path):
    return str(path)
  else:
    parent, start, end = path
    return f"{parent},{start},{end}"

def to_absolute(paths: PathTuple) -> tuple[Path, Path]:
  parent, start0, end0 = paths
  start = Path(
    steps=parent.steps + start0.steps,
    offset=start0.offset,
  )
  end = Path(
    steps=parent.steps + end0.steps,
    offset=end0.offset,
  )
  return start, end
  
def _capture_cfi(path: str):
  matched = re.search(r"(#|^)epubcfi\((.*)\)$", path)
  if matched:
    return matched.group(), matched.group(2)
  else:
    return None, None