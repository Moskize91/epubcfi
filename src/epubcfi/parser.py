import re

class EpubCFI:
  pass

def parse(path: str):
  cfi = _capture_cfi(path)
  if cfi is None:
    return
  
  
def _capture_cfi(path: str):
  matched = re.search(r"(#|^)epubcfi\((.*)\)$", path)
  if matched:
    return matched.group(2)