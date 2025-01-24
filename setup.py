from setuptools import setup, find_packages

setup(
  name="epubcfi",
  version="0.0.6",
  author="Tao Zeyu",
  author_email="i@taozeyu.com",
  description="handle Epub CFI",
  packages=find_packages(),
  long_description=open("./README.md", encoding="utf8").read(),
  long_description_content_type="text/markdown",
  install_requires=[
    "lxml>=5.3.0,<6.0",
  ],
)