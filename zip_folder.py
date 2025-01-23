import os
import zipfile

def main():
  project_path = os.path.dirname(os.path.abspath(__file__))
  folder_path = os.path.join(project_path, "tests", "epub", "assets", "sample.epub")
  zip_path = os.path.join(project_path, "tests", "epub", "assets", "zip_sample.epub")

  with open(zip_path, "wb") as file:
    with zipfile.ZipFile(file, "w") as zip_file:
      for root, _, files in os.walk(folder_path):
        for file in files:
          file_path = os.path.join(root, file)
          relative_path = os.path.relpath(file_path, folder_path)
          zip_file.write(file_path, arcname=relative_path)

if __name__ == "__main__":
  main()