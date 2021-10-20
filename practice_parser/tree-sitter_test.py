from tree_sitter import Language, Parser
import sys 

Language.build_library(
  # Store the library in the `build` directory
  'build/my-languages.so',

  # Include one or more languages
  [
    '/Users/tessiebaumann/tree-sitter-python'
    # '/Users/tessiebaumann/Library/Mobile Documents/com~apple~CloudDocs/Software Engineering/tree-sitter-java'
  ]
)

PY_LANGUAGE = Language('build/my-languages.so', 'python')
# JAVA_LANGUAGE = Language('build/my-languages.so', 'java')

parser_py = Parser()
# parser_java = Parser()

parser_py.set_language(PY_LANGUAGE)
# parser_java.set_language(JAVA_LANGUAGE)

test_py = open('test.py', 'r')
# test_java = open('test.java', 'r')

tree_py = parser_py.parse(bytes('test_py', "utf8"))
# tree_java = parser_java.parse(bytes(test_java, "utf8"))


# endFile = open("endFile.txt", 'w')
# endFile.write(tree_py)
# endFile.close()


