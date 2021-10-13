from tree_sitter import Language, Parser
import sys 

Language.build_library(
  # Store the library in the `build` directory
  'build/my-languages.so',

  # Include one or more languages
  [
    'vendor/tree-sitter-python'
  ]
)

PY_LANGUAGE = Language('build/my-languages.so', 'python')

parser = Parser()
parser.set_language(PY_LANGUAGE)

test = open('test.py', 'r')

tree = parser.parse(bytes("""
def foo():
    if bar:
        baz()
""", "utf8"))

