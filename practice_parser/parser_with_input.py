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
  (function_definition) @function.definition
  (call) @method.call
  """)
  print_method_dict_with_queries(query)
    
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
        calls[method_name] = method_calls
      method_name = "".join([line for line in lines[capture[0].start_point[0]:capture[0].end_point[0] + 1]])
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
  calls['global'] = globals
  for call in calls.items():
    print(call)

# The following code is a breadth-first search of the tree by adding the children of all the nodes
# currently in the children list to it.  It only terminates when there are no more children to add.

def main():
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