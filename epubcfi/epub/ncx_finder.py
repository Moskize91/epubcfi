import os

from ..cfi import Step, Redirect, Path, PathRange, ParsedPath
from .picker import EpubBook
from .stepper import forward_steps
from .utils import relative_root_path

def find_ncx_label(book: EpubBook, reader: any, path: ParsedPath):
  steps = _pick_steps(path)
  if steps is None:
    # never redirect. it means it's not a article file.
    return None

  tags_stack = forward_steps(reader, steps)
  if len(tags_stack) == 0:
    # match failed
    return None

  _, attrs = tags_stack[-1]
  href = _pick_href(book, attrs)
  if href is None:
    return None

  href = href.strip()
  path = relative_root_path(
    root_path=book.root_path,
    base_path=os.path.dirname(book.content_path),
    href=href,
  )
  for label, ncx_path in book.ncx:
    if path == ncx_path:
      return label

  return None

def _pick_steps(path: ParsedPath) -> list[int] | None:
  steps: list[int] = []
  found_redirect: bool = False

  if isinstance(path, Path):
    for step in path.steps:
      if isinstance(step, Step):
        steps.append(step.index)
      else:
        found_redirect = True
        break
  elif isinstance(path, PathRange):
    for step in path.parent.steps:
      if isinstance(step, Step):
        steps.append(step.index)
      else:
        found_redirect = True
        break
    if not found_redirect:
      found_redirect = isinstance(path.start.steps[0], Redirect)

  if not found_redirect:
    return None
  return steps

def _pick_href(book: EpubBook, attrs: dict[str, str]) -> str | None:
  href = attrs.get("href", None)
  if href is not None:
    return href

  idref = attrs.get("idref", None)
  if idref is None:
    return None

  return book.ref2path.get(idref, None)