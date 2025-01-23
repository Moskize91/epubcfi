import os

from lxml import etree
from ..cfi import Step, Redirect


class Spine:
  def __init__(self, folder_path, base_path, item):
    self._folder_path = folder_path
    self._base_path = base_path
    self.href = item.get("href")
    self.media_type = item.get("media-type")

  @property
  def path(self) -> str:
    path = os.path.join(self._base_path, self.href)
    path = os.path.abspath(path)

    if os.path.exists(path):
      return path

    path = os.path.join(self._folder_path, self.href)
    path = os.path.abspath(path)
    return path


class Cursor:
  def __init__(self, dom: any):
    self.dom: any = dom

  def forward(self, operation: Step | Redirect):
    if isinstance(operation, Step):
      self._step(operation)
    elif isinstance(operation, Redirect):
      self._redirect(operation)
    else:
      raise ValueError(f"Unexpected operation: {operation}")


  def _step(self, step: Step):
    # https://idpf.org/epub/linking/cfi/epub-cfi.html#sec-path-child-ref
    for child in self.dom.iterchildren():
      print(child)

  def _redirect(self, redirect: Redirect):
    pass


class Picker:
  def __init__(self, folder_path: str):
    self.folder_path = folder_path
    self._content_path = self._find_content_path(folder_path)
    self._tree = etree.parse(self._content_path)
    self._namespaces = { "ns": self._tree.getroot().nsmap.get(None) }
    self._spine = self._tree.xpath("//ns:spine", namespaces=self._namespaces)[0]
    self._metadata = self._tree.xpath("//ns:metadata", namespaces=self._namespaces)[0]
    self._manifest = self._tree.xpath("//ns:manifest", namespaces=self._namespaces)[0]

  def _find_content_path(self, path: str) -> str:
    root = etree.parse(os.path.join(path, "META-INF", "container.xml")).getroot()
    rootfile = root.xpath(
      "//ns:container/ns:rootfiles/ns:rootfile",
      namespaces={ "ns": root.nsmap.get(None) },
    )[0]
    full_path = rootfile.attrib["full-path"]
    joined_path = os.path.join(path, full_path)

    return os.path.abspath(joined_path)

  @property
  def ncx_path(self) -> str | None:
    ncx_dom = self._manifest.find(".//*[@id=\"ncx\"]")
    if ncx_dom is None:
      return None

    href_path = ncx_dom.get("href")
    base_path = os.path.dirname(self._content_path)
    path = os.path.join(base_path, href_path)
    path = os.path.abspath(path)

    if os.path.exists(path):
      return path

    path = os.path.join(self.folder_path, path)
    path = os.path.abspath(path)
    return path

  @property
  def title(self):
    titles = self._metadata.xpath(
      "./dc:title",
      namespaces={
        "dc": self._metadata.nsmap.get("dc"),
      },
    )
    if len(titles) == 0:
      return None

    return titles[0].text

  @property
  def authors(self) -> list[str]:
    creators = self._metadata.xpath(
      "./dc:creator",
      namespaces={
        "dc": self._metadata.nsmap.get("dc"),
      },
    )
    return [creator.text for creator in creators]

  def cursor(self) -> Cursor:
    return Cursor(self._tree.getroot())

  @property
  def spines(self) -> list[Spine]:
    idref_dict = {}
    index = 0

    for child in self._spine.iterchildren():
      id = child.get("idref")
      idref_dict[id] = index
      index += 1

    items = [None for _ in range(index)]
    spines: list[Spine] = []

    for child in self._manifest.iterchildren():
      id = child.get("id")
      if id in idref_dict:
        index = idref_dict[id]
        items[index] = child

    base_path = os.path.dirname(self._content_path)

    for item in items:
      if item is not None:
        spines.append(Spine(
          folder_path=self.folder_path,
          base_path=base_path,
          item=item,
        ))

    return spines