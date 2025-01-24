import os
from typing import Iterable, TypeVar, Generic, Callable

def relative_root_path(root_path: str, base_path: str, href: str):
  if not root_path.endswith(os.path.sep):
    root_path = root_path + os.path.sep

  path = os.path.join(base_path, href)
  path = os.path.abspath(path)

  if not os.path.exists(path):
    path = os.path.join(root_path, href)
    path = os.path.abspath(path)

  if not path.startswith(root_path):
    return path

  path = path[len(root_path):]
  path = "." + os.path.sep + path

  return path

E = TypeVar("E")

class SizeLimitMap(Generic[E]):
  def __init__(self, limit: int, on_close: Callable[[E], None]):
    super().__init__()
    self._store: dict[str, E] = {}
    self._keys: list[str] = []
    self._limit: int = limit
    self._on_close: Callable[[E], None] = on_close

  def items(self) -> Iterable[tuple[str, E]]:
    return self._store.items()

  def keys(self) -> Iterable[str]:
    return iter(self._keys)

  def values(self) -> Iterable[E]:
    return self._store.values()

  def get(self, key: str) -> E | None:
    return self._store.get(key, None)

  def __len__(self):
    return len(self._store)

  def __contains__(self, item: E):
    return item in self._store

  def __str__(self):
    return str(self._store)

  def __setitem__(self, key: str, value: E):
    removed_value: E | None = None

    if key not in self._store:
      self._keys.append(key)
      if len(self._keys) > self._limit:
        removed_key = self._keys.pop(0)
        removed_value = self._store.pop(removed_key)

    self._store[key] = value
    if removed_value is not None:
      self._on_close(removed_value)

  def __getitem__(self, key: str) -> E | None:
    if key not in self._store:
      return None
    self._keys.remove(key)
    return self._store.pop(key)