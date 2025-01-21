class EpubCFIException(Exception):
  def __init__(self, message: str):
    super().__init__(message)

class ParserException(EpubCFIException):
  pass

class TokenizerException(Exception):
  pass
