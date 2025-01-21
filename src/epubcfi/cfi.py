import re
from .parser import parse, Path

def split(path: str) -> tuple[str, None | Path | tuple[Path, Path, Path]]:
  tail, cfi = _capture_cfi(path)
  if cfi is None:
    return path, None
  result = parse(cfi)
  prefix = path[:len(path) - len(tail)]
  return prefix, result

def to_absolute(paths: tuple[Path, Path, Path]) -> tuple[Path, Path]:
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