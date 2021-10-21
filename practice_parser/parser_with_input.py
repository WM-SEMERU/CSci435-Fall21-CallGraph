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
def parse_python(file):
    parser.set_language(PY_LANGUAGE)
    src_code = file.read()
    lines = src_code.split('\n')
    
    tree = parser.parse(bytes(src_code, "utf8"))

    root_node = tree.root_node
    classes, methods, calls = breath_search_tree(root_node, lines)
    print(classes, end = '\n\n')
    print(methods, end = '\n\n')
    print(calls, end = '\n\n')
    
# The following code is a breath-first search of the tree by adding the children of all the nodes
# currently in the children list to it.  It only terminates when there are no more children to add.
def breath_search_tree(root_node,lines) -> list:
    classes = []
    methods = []
    calls = []
    children = root_node.children # initializes the list to parse
    while len(children) > 0:
      for child in children:
        if child.type == 'class_definition':  # adds all class names to a list
          name = child.children[1]
          classes.append(lines[name.start_point[0]][name.start_point[1]:name.end_point[1]])
        elif child.type == 'function_definition':  # adds all method names to a list
          name = child.children[1]
          methods.append(lines[name.start_point[0]][name.start_point[1]:name.end_point[1]])
        elif child.type == 'expression_statement' and child.children[0].type == 'call':  # adds all method calls to a list
          call_line = child.children[0]
          calls.append(lines[call_line.start_point[0]][call_line.start_point[1]:call_line.end_point[1]])
        if len(child.children) > 0:         # adds all this nodes children to the list of nodes to parse
          children.extend(child.children)   # 
        children.remove(child)              # removes the current node
    return classes, methods, calls
    
    
# TODO method to parse java code
def parse_java(src_code):   
    parser.set_language(JAVA_LANGUAGE)
    print(src_code)

    tree = parser.parse(bytes(src_code, "utf8"))


# main method handles command line input and/or user input for the filepath and the language of the file to be parsed
# Currently only supports parsing of 1 file at a time
# command line arguments: [filepath] [language]
def main():  
  if len(sys.argv) == 1:                                   # if there are no arguments passed to the command line take user input
    filepath = input("What is the filepath of the file? ")
  else:
    filepath = sys.argv[1]
  file = open(filepath, 'r')        # read-only file

  if ".py" in filepath:
      parse_python(file)
  elif ".java" in filepath:
      parse_java(file)


if __name__ == '__main__':
  main()