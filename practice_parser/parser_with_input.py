import sys
import os
from tree_sitter import Language, Parser


"""tree sitter setup code"""
Language.build_library(
    'build/my-languages.so',
    [
        'vendor/tree-sitter-python',
        'vendor/tree-sitter-java'
    ]
)

PY_LANGUAGE = Language('build/my-languages.so', 'python')
JAVA_LANGUAGE = Language('build/my-languages.so', 'java')  # In case people want to work on java functionality

parser = Parser()
"""----------------------"""

# TODO method to parse python code
def parse_python(file):
    parser.set_language(PY_LANGUAGE)
    print("hello")
    src_code = file.read()
    print(src_code)
    lines = src_code.split('\n')
    
    tree = parser.parse(bytes(src_code, "utf8"))

    root_node = tree.root_node
    print(root_node)
    
  
    
# TODO method to parse java code
def parse_java(src_code):   
    parser.set_language(JAVA_LANGUAGE)
    print(src_code)

    tree = parser.parse(bytes(src_code, "utf8"))


# main method handles command line input and/or user input for the filepath and the language of the file to be parsed
# Currently only supports parsing of 1 file at a time
# command line arguments: [filepath] [language]
def main():

  cmd_line_args = sys.argv[1:] # cmd_line_args[0] = [filepath] and cmd_line_args[1] = [language]
  
  filepath = ""

  if len(cmd_line_args) == 0:                                   # if there are no arguments passed to the command line take user input
    filepath = input("What is the filepath of the file?" )
    language = input("What language is the file coded in? ").lower()
  elif len(cmd_line_args) == 1:                                 # if only the language is passed to the command line
    filepath = cmd_line_args[0]
    language = input("What language is the file coded in? ").lower()
  else:                                                         # if both are passed to the command line
    filepath = cmd_line_args[0]
    language = cmd_line_args[1].lower()
  
  file = open(filepath, 'r')        # read-only file


  # choose language to parse based on input
  if language == 'python' or 'py':
      parse_python(file)
  elif language == 'java' or 'jv':
      parse_java(file)


if __name__ == '__main__':
  main()