import os
import io

from dataclasses import dataclass
from lxml import etree
from .utils import relative_root_path


@dataclass
class EpubBook:
  title: str | None
  authors: list[str]
  root_path: str
  content_path: str
  ncx: list[tuple[str, str]]
  ref2path: dict[str, str]

def pick(root_path: str) -> EpubBook:
  content_path = _find_content_path(root_path)
  content_tree = etree.parse(content_path)
  base_path = os.path.dirname(content_path)
  title, authors = _find_metadata(content_tree)
  ncx_path = _find_ncx_path(content_tree, root_path, content_path)
  ref2path: dict[str, str] = {}
  ncx: list[tuple[str, str]] = []

  for id, href in _find_refs(content_tree):
    path = relative_root_path(root_path, base_path, href)
    ref2path[id] = path

  for label, href in _find_ncx(ncx_path):
    path = relative_root_path(root_path, base_path, href)
    ncx.append((label, path))

  return EpubBook(
    title=title,
    authors=authors,
    root_path=root_path,
    content_path=content_path,
    ref2path=ref2path,
    ncx=ncx,
  )

def _find_content_path(root_path: str) -> str:
  root = etree.parse(os.path.join(root_path, "META-INF", "container.xml")).getroot()
  rootfile = root.xpath(
    "//ns:container/ns:rootfiles/ns:rootfile",
    namespaces={ "ns": root.nsmap.get(None) },
  )[0]
  full_path = rootfile.attrib["full-path"]
  joined_path = os.path.join(root_path, full_path)

  return os.path.abspath(joined_path)

def _find_ncx_path(tree: any, root_path: str, content_path: str):
  manifest = tree.xpath(
    "//ns:manifest",
    namespaces=_namespaces(tree),
  )[0]
  ncx_dom = manifest.find(".//*[@id=\"ncx\"]")
  if ncx_dom is None:
    return None

  href_path = ncx_dom.get("href")
  base_path = os.path.dirname(content_path)
  path = os.path.join(base_path, href_path)
  path = os.path.abspath(path)

  if os.path.exists(path):
    return path

  path = os.path.join(root_path, path)
  path = os.path.abspath(path)
  return path

def _find_metadata(tree: any):
  metadata = tree.xpath("//ns:metadata", namespaces=_namespaces(tree))[0]
  titles = metadata.xpath(
    "./dc:title",
    namespaces={
      "dc": metadata.nsmap.get("dc"),
    },
  )
  creators = metadata.xpath(
    "./dc:creator",
    namespaces={
      "dc": metadata.nsmap.get("dc"),
    },
  )
  title: str | None = None
  authors: list[str] = [creator.text for creator in creators]

  if len(titles) > 0:
    title = titles[0].text

  return title, authors

def _find_refs(tree: any):
  namespaces = _namespaces(tree)
  spine = tree.xpath("//ns:spine", namespaces=namespaces)[0]
  manifest = tree.xpath("//ns:manifest", namespaces=namespaces)[0]
  idrefs: set[str] = set()

  for child in spine.xpath(".//ns:itemref", namespaces=namespaces):
    idref = child.get("idref", None)
    if idref is not None:
      idrefs.add(idref.strip())

  for child in manifest.xpath(".//ns:item", namespaces=namespaces):
    id = child.get("id", None)
    href = child.get("href", None)

    if id is None:
      continue
    if href is None:
      continue
    if id in idrefs:
      yield id, href.strip()

def _find_ncx(ncx_path: str):
  tree = etree.parse(ncx_path)
  namespaces = _namespaces(tree)
  for nav_point in tree.xpath("//ns:navPoint", namespaces=namespaces):
    label_dom = nav_point.xpath(".//ns:navLabel", namespaces=namespaces)[0]
    content_dom = nav_point.xpath(".//ns:content", namespaces=namespaces)[0]
    label_buffer = io.StringIO()

    for text_dom in label_dom.xpath(".//ns:text", namespaces=namespaces):
      label_buffer.write(text_dom.text)

    label = label_buffer.getvalue().strip()
    href = content_dom.get("src", None)

    if href is not None:
      yield label, href.strip()

def _namespaces(tree: any):
  return { "ns": tree.getroot().nsmap.get(None) }
