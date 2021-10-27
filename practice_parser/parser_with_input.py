import sys
import os
import pandas as pd
from typing import Tuple
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

# Every node in the tree has 4 attributes:
# A type (like "function_definition" for methods, "expression_statement" for lines in a method, or "class_definition" for classes)
# A start point which comes in the form of a tuple where the line number is index 0 and 
#         the character number is index 1 (node.start_point[0] and node.start_point[1])
# An end point that is formatted the same way as the start point (node.end_point).
# A list of children (Using the tree-sitter playground is useful, the amount of indentation indicate a child-parent relationship).
# 
# There are also methods like get_sibling and get_parent and such but I haven't used any of those for parsing.

# TODO method to parse python code
def parse_python_with_queries():
  parser.set_language(PY_LANGUAGE)
  global tree
  tree = parser.parse(bytes(src_code, "utf8"))


  #"""
  query = PY_LANGUAGE.query("""
  (function_definition 
    body: (block
      (expression_statement 
        (call)? @method.call
        (assignment 
          (call)? @method.call)?)?)) @function.definition
  (call) @method.call
  """)
  print_method_dict_with_queries(query)
  query = PY_LANGUAGE.query("""
  (call) @call
  """)
  print_method_dict_with_queries_v2(query)

# TODO method to parse java code
def parse_java_with_queries():
  parser.set_language(JAVA_LANGUAGE)
  global tree
  tree = parser.parse(bytes(src_code, "utf8"))

  query = JAVA_LANGUAGE.query("""
  (method_declaration) @function.definition
  
  (constructor_declaration) @function.definition

  (object_creation_expression) @method.call

  (method_invocation) @method.call
  """)

  print_method_dict_with_queries(query)
  query = JAVA_LANGUAGE.query("""
  (object_creation_expression) @call

  (method_invocation) @call
  """)
  print_method_dict_with_queries_v2(query)

# find all function_definitions
# walk through them and find all the calls in the children

def print_method_dict_with_queries(query):
  captures = query.captures(tree.root_node)
  calls = {}
  method_calls = []
  globals = []
  method_name = ''
  start_line = 0
  end_line = 0
  for capture in captures:   
    if capture[1] == 'function.definition':
      if method_name != '':
        calls[method_name] = set(method_calls)
      name_node = capture[0].child_by_field_name('name')    # get its name
      method_name = lines[name_node.start_point[0]][name_node.start_point[1]:name_node.end_point[1]]
      #method_name = "".join([line for line in lines[capture[0].start_point[0]:capture[0].end_point[0] + 1]]) 
      start_line = capture[0].start_point[0]
      end_line = capture[0].end_point[0] + 1
      method_calls = []
    elif capture[1] == 'method.call':
      
      line_num = capture[0].start_point[0]
      call = lines[line_num][capture[0].start_point[1]:capture[0].end_point[1]]
      if start_line < line_num < end_line:
        method_calls.append(call)
      else:
        globals.append(call)
  calls[method_name] = set(method_calls)
  calls['global'] = globals
  for call in calls.items():
    print(call)#'''

def print_method_dict_with_queries_v2(query):
  captures = query.captures(tree.root_node)
  for capture in captures:

    pass

  pass

def main():
  global filepath
  if len(sys.argv) == 1:                                    # if there are no arguments passed to the command line take user input
    filepath = input("What is the filepath of the file? ")
  else:
    filepath = sys.argv[1]                                  # take command line input for file to parse
  file = open(filepath, 'r')                                # read-only file

  global src_code, lines
  src_code = file.read()
  lines = src_code.split('\n')

  if ".py" in filepath:
    parse_python_with_queries()
  elif ".java" in filepath:
    parse_java_with_queries()


if __name__ == '__main__':
  main()