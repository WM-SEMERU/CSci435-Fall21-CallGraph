import sys
import os
from tree_sitter import Language, Parser


"""tree sitter setup code"""
Language.build_library(
    'build/my-languages.so',
    [
        'vendor/tree-sitter-python',
        #'vendor/tree-sitter-java'
    ]
)

PY_LANGUAGE = Language('build/my-languages.so', 'python')
#JAVA_LANGUAGE = Language('build/my-languages.so', 'java')  # In case people want to work on java functionality

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
def parse_python():
  parser.set_language(PY_LANGUAGE)
  global tree
  tree = parser.parse(bytes(src_code, "utf8"))
  
  query = PY_LANGUAGE.query("""
  (function_definition
  name: (identifier) @function.def
  body: (block) @function.body)

  

  (call
    function: (identifier) @function.call)
  """)
  captures = query.captures(tree.root_node)
  for capture in captures:
    print(capture)
    #line = lines[capture[0].start_point[0]]
    #print(line[capture[0].start_point[1]:capture[0].end_point[1]])
  """
  classes, methods, calls = breadth_search_tree('class_definition', 'function_definition', 'call')
  method_call_dict = get_method_call_dict(methods)
  print(method_call_dict)
  #print(classes, end = '\n\n')
  #print(methods, end = '\n\n')
  #print(calls, end = '\n\n')
  #"""
    
# TODO method to parse java code
def parse_java():
  #parser.set_language(JAVA_LANGUAGE)
  global tree
  tree = parser.parse(bytes(src_code, "utf8"))

  classes, methods, calls = breadth_search_tree('class_declaration', 'method_declaration', 'method_invocation')
  method_call_dict = get_method_call_dict(methods)
  print(method_call_dict)
  #print(classes, end = '\n\n')
  #print(methods, end = '\n\n')
  #print(calls, end = '\n\n')

# The following code is a breadth-first search of the tree by adding the children of all the nodes
# currently in the children list to it.  It only terminates when there are no more children to add.
def breadth_search_tree(name_of_class, name_of_method, name_of_method_call) -> list:
  root_node = tree.root_node
  classes = []
  methods = []
  calls = []
  children = root_node.children # initializes the list to parse
  while len(children) > 0:
    for child in children:

      add_children = True
      child_type = child.type
      # I wish there were switch statements in python
      if child_type == name_of_class:  # if its a class
        name_node = child.child_by_field_name('name')    # get its name
        name = lines[name_node.start_point[0]][name_node.start_point[1]:name_node.end_point[1]]
        classes.append(child)
      elif child_type == name_of_method:  # if its a method
        #lines_n = [line + "\n" for line in lines[child.start_point[0]:child.end_point[0] + 1]] # adds a "\n" character back to the end of every line
        #name = "".join(lines_n)
        methods.append(child)
        add_children = False
      elif child_type == name_of_method_call:  # if its a method call
        call_name = lines[child.start_point[0]][child.start_point[1]:child.end_point[1]]
        calls.append(call_name)
      
      
      if len(child.children) > 0 and add_children:         # adds all this nodes children to the list of nodes to parse
        children.extend(child.children)   # 
      children.remove(child)              # removes the current node
  return classes, methods, calls

def get_method_call_dict(methods) -> dict:
  ret = {}
  for method in methods:
    #lines_n = [line + "\n" for line in lines[method.start_point[0]:method.end_point[0] + 1]] # adds a "\n" character back to the end of every line
    #name = "".join(lines_n)
    method_calls = []
    children = method.child_by_field_name('body').children
    while len(children) > 0:
      for child in children:

        if child.type == 'call':
          method_calls.append(lines[child.start_point[0]][child.start_point[1]:child.end_point[1]])

        if len(child.children) > 0:         # adds all this nodes children to the list of nodes to parse
          children.extend(child.children)   # 
        children.remove(child)              # removes the current node
    name_node = method.child_by_field_name('name')    # get its name
    name = lines[name_node.start_point[0]][name_node.start_point[1]:name_node.end_point[1]]
    ret[name] = method_calls
  return ret

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
    parse_python()
  elif ".java" in filepath:
    parse_java()


if __name__ == '__main__':
  main()