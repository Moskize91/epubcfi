import unittest

try:
  loader = unittest.TestLoader()
  suite = loader.discover("tests")
  # suite = loader.discover("tests", pattern="test_epub.py")
  runner = unittest.TextTestRunner()
  result = runner.run(suite)
  if not result.wasSuccessful():
    # pylint: disable=consider-using-sys-exit
    exit(1)

# pylint: disable=broad-exception-caught
except Exception as e:
  print(e)
  # pylint: disable=consider-using-sys-exit
  exit(1)
