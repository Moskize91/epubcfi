from dataclasses import dataclass
from xml.parsers.expat import ParserCreate

@dataclass
class _State:
  name: str
  attrs: dict[str, str]
  index: int

# https://idpf.org/epub/linking/cfi/epub-cfi.html#sec-path-child-ref
class _Cursor:
  def __init__(self, reader: any, steps: list[int]):
    self._reader: any = reader
    self._step_queue: list[int] = self._create_step_queue(steps)
    self._step_deep: int = 0
    self._stack: list[_State] = []
    self._matched: bool = False
    self._last_is_text: bool = False
    self._index: int = 0
    self._parser = ParserCreate()
    self._parser.StartElementHandler = self._start_element
    self._parser.EndElementHandler = self._end_element
    self._parser.CharacterDataHandler = self._char_data

  def _create_step_queue(self, steps: list[int]):
    # 2 means the root element
    return [*reversed(steps), 2]

  def parse(self):
    try:
      self._parser.ParseFile(self._reader)
    except StopIteration:
      pass
    if not self._matched:
      return []
    return [
      (state.name, state.attrs)
      for state in self._stack
    ]

  def _start_element(self, name: str, attrs: dict[str, str]):
    # Child [XML] elements are assigned even indices
    self._index += 1
    if self._index % 2 != 0:
      self._index += 1
    state = _State(name, attrs, self._index)
    self._stack.append(state)
    self._index = 0
    self._last_is_text = False

    if self._step_deep == len(self._stack) - 1:
      step = self._step_queue[-1]
      if step == state.index:
        self._step_queue.pop()
        if len(self._step_queue) == 0:
          self._matched = True
          raise StopIteration()
        self._step_deep += 1

  def _end_element(self, name: str):
    state = self._stack.pop()
    assert state is not None
    assert state.name == name
    self._index = state.index
    self._last_is_text = False
    if len(self._stack) < self._step_deep:
      # won't match anymore
      raise StopIteration()

  def _char_data(self, _: str):
    # Consecutive (potentially-empty) chunks of character
    # data are each assigned odd indices (i.e., starting at 1, followed by 3, etc.).
    if self._last_is_text:
      return
    self._index += 1
    self._last_is_text = True
    if self._index % 2 == 0:
      self._index += 1

def forward_steps(reader: any, steps: list[int]) -> list[tuple[str, dict[str, str]]]:
  return _Cursor(reader, steps).parse()