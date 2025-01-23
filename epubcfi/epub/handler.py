import os
import tempfile
import shutil

from io import TextIOWrapper
from ..cfi import ParsedPath
from .unzip import Unzip
from .picker import pick, EpubBook
from .ncx_finder import find_ncx_label
from .utils import SizeLimitMap


class EpubNode:
  def __init__(
      self,
      cache_path: str | None = None,
      remove_cache_path: bool = False,
    ):
    self._is_created_path: bool = False
    unzip_path = self._norm_cache_path(cache_path)
    if remove_cache_path or unzip_path != cache_path:
      self._is_created_path = True

    self._unzip: Unzip = Unzip(unzip_path)
    self._books: SizeLimitMap[tuple[EpubBook, TextIOWrapper]] = SizeLimitMap(
      limit=7,
      on_close=lambda e: e[1].close(),
    )

  def ncx_label(self, epub_path: str, cfi_path: ParsedPath) -> str | None:
    book, reader = self._book_pair(epub_path)
    reader.seek(0)
    label = find_ncx_label(book, reader, cfi_path)
    return label

  def _norm_cache_path(self, cache_path: str | None) -> None:
    if cache_path is None:
      cache_path = tempfile.mkdtemp()
    elif not os.path.exists(cache_path):
      os.makedirs(cache_path)
    elif not os.path.isdir(cache_path):
      raise NotADirectoryError(f"Path is not a directory: {cache_path}")
    return cache_path

  def __enter__(self) -> "EpubNode":
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    for _, reader in self._books.values():
      reader.close()
    if self._is_created_path:
      shutil.rmtree(self._unzip._unzip_path)

  def _book_pair(self, path: str) -> tuple[EpubBook, TextIOWrapper]:
    path = os.path.abspath(path)
    if path not in self._books:
      dir_path = self._unzip.unzip_file(path)
      book = pick(dir_path)
      reader = open(book.content_path, "rb")
      self._books[path] = (book, reader)
    return self._books[path]