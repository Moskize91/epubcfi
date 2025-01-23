import os

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