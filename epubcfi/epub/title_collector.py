from dataclasses import dataclass
from xml.parsers.expat import ParserCreate

@dataclass
class _State:
  name: str
  attrs: dict[str, str]
  index: int

# https://idpf.org/epub/linking/cfi/epub-cfi.html#sec-path-child-ref
class _FireCursor:
  def __init__(self, file_path: str, steps: list[int]):
    self._file_path = file_path
    self._step_queue: list[int] = self._create_step_queue(steps)
    self._step_deep: int = 0
    self._stack: list[_State] = []
    self._title: str | None = None
    self._read_title_content: bool = False
    self._matched: _State | None = None
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
      with open(self._file_path, "rb") as file:
        self._parser.ParseFile(file)
    except StopIteration:
      pass
    if self._matched is None:
      return None
    return self._matched.name, self._matched.attrs, self._title

  def _start_element(self, name: str, attrs: dict[str, str]):
    # Child [XML] elements are assigned even indices
    self._index += 1
    if self._index % 2 != 0:
      self._index += 1
    state = _State(name, attrs, self._index)
    self._stack.append(state)
    self._index = 0

    if self._title is None:
      self._check_find_title(state)

    if self._matched is None:
      self._check_find_matched(state)
      self._stop_if_collect_success()

  def _end_element(self, name: str):
    state = self._stack.pop()
    assert state is not None
    assert state.name == name
    self._index = state.index
    if len(self._stack) < self._step_deep:
      # won't match anymore
      raise StopIteration()

  def _char_data(self, text: str):
    # Consecutive (potentially-empty) chunks of character
    # data are each assigned odd indices (i.e., starting at 1, followed by 3, etc.).
    self._index += 1
    if self._index % 2 == 0:
      self._index += 1

    if self._read_title_content:
      self._title = text
      self._read_title_content = False
      self._stop_if_collect_success()

  def _check_find_title(self, state: _State):
    if state.name != "title":
      return
    stack_names = tuple(state.name for state in self._stack)
    if stack_names != ("html", "head", "title"):
      return
    self._read_title_content = True

  def _check_find_matched(self, state: _State):
    if self._step_deep != len(self._stack) - 1:
      return
    step = self._step_queue[-1]
    if step != state.index:
      return
    self._step_queue.pop()
    if len(self._step_queue) != 0:
      self._step_deep += 1
      return
    self._matched = state

  def _stop_if_collect_success(self):
    if self._title is not None and self._matched is not None:
      raise StopIteration()