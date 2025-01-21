from __future__ import annotations
from dataclasses import dataclass
from io import StringIO
from typing import Literal
from .error import ParserException
from .tokenizer import (
  EOF,
  Step,
  Symbol,
  Token,
  Tokenizer,
  Offset as TokenOffset,
  CharacterOffset,
  TemporalOffset,
  SpatialOffset,
  TemporalSpatialOffset,
)

Offset = CharacterOffset | TemporalOffset | SpatialOffset | TemporalSpatialOffset

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

@dataclass
class Redirect:
  def __str__(self) -> str:
    return "!"

class _Parser:
  def __init__(self, content: str):
    self._cache_token: Token | None = None
    self._tokenizer: Tokenizer = Tokenizer(content)

  def parse(self) -> Path | tuple[Path, Path, Path]:
    paths = list(self._search_path())
    if len(paths) == 1:
      return paths[0]
    elif len(paths) == 3:
      # https://idpf.org/epub/linking/cfi/epub-cfi.html#sec-ranges
      parent, start, end = paths
      if parent.start_with_redirect():
        raise ParserException("Parent path cannot start with \"!\")")
      return parent, start, end
    else:
      raise ParserException(f"wrong path number: {len(paths)}")

  def _search_path(self):
    while True:
      path = self._parse_path()
      if path is None:
        raise ParserException(f"Unexpected token: {self._token}")

      yield path
      tail = self._token

      if isinstance(tail, Symbol) and tail.text == ",":
        self._forward()
      elif isinstance(tail, EOF):
        break
      else:
        raise ParserException(f"Unexpected token: {tail}")

  def _parse_path(self) -> Path | None:
    steps: list[Redirect | Step] = []
    offset: Offset | None = None

    while True:
      token = self._token
      if isinstance(token, Step):
        steps.append(token)
      elif isinstance(token, Symbol) and token.text == "!":
        if len(steps) > 0 and isinstance(steps[-1], Redirect):
          raise ParserException("Two consecutive redirects")
        steps.append(Redirect())
      else:
        break
      self._forward()
    
    if len(steps) == 0:
      return None

    if isinstance(self._token, TokenOffset):
      offset = self._token
      self._forward()

    if offset is None and isinstance(self._token, Symbol) and self._token.text == "!":
      # 参考 https://idpf.org/epub/linking/cfi/epub-cfi.html#sec-epubcfi-syntax
      # 从公式 redirected_path	=	"!" , ( offset | path ); 可知：
      # 不可以 ! 作为结尾，这样会选到某个文件的 root 节点（这是禁止的）
      raise ParserException("Cannot select root dom (must offset after redirect symbol)")
    
    return Path(steps=steps, offset=offset)

  def _is_symbol(self, symbol: Literal["!", ","]) -> bool:
    token = self._token
    if not isinstance(token, Symbol):
      return False
    return token.text == symbol

  @property
  def _token(self) -> Token:
    if self._cache_token is None:
      self._forward()
    return self._cache_token

  def _forward(self):
    if isinstance(self._cache_token, EOF):
      return
    while True:
      self._cache_token = self._tokenizer.read()
      if self._cache_token is not None:
        break

def parse(content: str) -> Path | tuple[Path, Path, Path]:
  return _Parser(content).parse()