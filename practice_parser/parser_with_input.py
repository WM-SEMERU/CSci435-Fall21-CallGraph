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
    classes, methods, calls = breath_search_tree(root_node, lines, 'class_definition', 'function_definition', 'call')
    print(classes, end = '\n\n')
    print(methods, end = '\n\n')
    print(calls, end = '\n\n')    
    
# TODO method to parse java code
def parse_java(file):   
    parser.set_language(JAVA_LANGUAGE)
    src_code = file.read()
    lines = src_code.split('\n')
    
    tree = parser.parse(bytes(src_code, "utf8"))

    root_node = tree.root_node
    classes, methods, calls = breath_search_tree(root_node, lines, 'class_declaration', 'method_declaration', 'method_invocation')
    print(classes, end = '\n\n')
    print(methods, end = '\n\n')
    print(calls, end = '\n\n')

# The following code is a breath-first search of the tree by adding the children of all the nodes
# currently in the children list to it.  It only terminates when there are no more children to add.
def breath_search_tree(root_node, lines, name_of_class, name_of_method, name_of_method_call) -> list:
    classes = []
    methods = []
    calls = []
    children = root_node.children # initializes the list to parse
    while len(children) > 0:
      for child in children:
                
        child_type = child.type
        if child_type == name_of_class:  # adds all class names to a list
          name_node = child.child_by_field_name('name')
          name = lines[name_node.start_point[0]][name_node.start_point[1]:name_node.end_point[1]]
          classes.append(name)
        elif child_type == name_of_method:  # adds all method names to a list
          lines_n = [line + "\n" for line in lines[child.start_point[0]:child.end_point[0] + 1]]
          name = "".join(lines_n)
          methods.append(name)
        elif child_type == 'expression_statement' and child.children[0].type == name_of_method_call:  # adds all method calls to a list
          call_name = lines[child.start_point[0]][child.start_point[1]:child.end_point[1]]
          calls.append(call_name)

        if len(child.children) > 0:         # adds all this nodes children to the list of nodes to parse
          children.extend(child.children)   # 
        children.remove(child)              # removes the current node
    return classes, methods, calls

def main():
  if len(sys.argv) == 1:                                    # if there are no arguments passed to the command line take user input
    filepath = input("What is the filepath of the file? ")
  else:
    filepath = sys.argv[1]                                  # take command line input for file to parse
  file = open(filepath, 'r')                                # read-only file

  if ".py" in filepath:
      parse_python(file)
  elif ".java" in filepath:
      parse_java(file)


if __name__ == '__main__':
  main()