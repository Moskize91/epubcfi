import os
import shutil
import hashlib
import zipfile

class Unzip:
  def __init__(self, unzip_path: str):
    self._unzip_path: str = unzip_path

  def unzip_file(self, file_path: str) -> str:
    if not os.path.exists(file_path):
      raise FileNotFoundError(f"File not found: {file_path}")
    if os.path.isdir(file_path):
      return file_path

    to_hash = f"{self._to_hash(file_path)}"
    to_path = os.path.join(self._unzip_path, to_hash)
    mtime_path = os.path.join(self._unzip_path, f"{to_hash}.mtime")

    if self._check_cache_exist(to_path):
      if self._check_mtime_match(mtime_path, file_path):
        return to_path
      shutil.rmtree(to_path)

    try:
      self._unzip(file_path, to_path)
    except Exception as e:
      shutil.rmtree(to_path)
      os.remove(mtime_path)
      raise e

    return to_path

  def _check_cache_exist(self, to_path: str) -> bool:
    if not os.path.exists(to_path):
      return False
    if os.path.isdir(to_path):
      return True
    os.remove(to_path)
    return False

  def _check_mtime_match(self, mtime_path: str, file_path: str) -> bool:
    mtime = str(os.path.getmtime(file_path))

    if not os.path.exists(mtime_path):
      return False

    if not os.path.isfile(mtime_path):
      shutil.rmtree(mtime_path)
      return False

    with open(mtime_path, "r", encoding="utf8") as file:
      if file.read() == mtime:
        return True

    with open(mtime_path, "w", encoding="utf8") as file:
      file.write(mtime)

    return False

  def _unzip(self, file_path: str, to_path: str):
    with zipfile.ZipFile(file_path, "r") as zip_ref:
      for member in zip_ref.namelist():
        target_path = os.path.join(to_path, member)
        if member.endswith("/"):
          os.makedirs(target_path, exist_ok=True)
        else:
          target_dir_path = os.path.dirname(target_path)
          os.makedirs(target_dir_path, exist_ok=True)
          with zip_ref.open(member) as source, open(target_path, "wb") as file:
            file.write(source.read())

  def _to_hash(self, text: str) -> str:
    sha512_hash = hashlib.sha512()
    sha512_hash.update(text.encode())
    return sha512_hash.hexdigest()