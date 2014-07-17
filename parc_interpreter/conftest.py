import pytest

def pytest_addoption(parser):
  parser.addoption( "--cpython", action="store_true",
                    help="use cpython" )

