import sys
import os
import pandas as pd
import numpy as np
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
JAVA_LANGUAGE = Language('build/my-languages.so', 'java') 

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


# Queries: 
# - anything in parenthesis is the type of the node you are trying to find.  
# - (call) for python means you are trying to find the method calls
# - the @ symbol is used when calling the capture method, anything without an @ symbol following it will be disregarded
# -    you wouldn't be able to use a query that's just (call) because it wouldn't return anything, but (call) @some-name would
# -    specifically, it would return a list of tuples where index 0 is the method call node and index 1 is "some-name"
# - by putting additional parenthesis in a set of parenthesis you denote a parent-child relationship between the two nodes:
# -    ex: (class_definition (identifier) ) indicates that (identifier) is a child of (class_definition)
# -    The same rules above apply to child nodes, so (class_definition (identifier) @some-name) would return the identifiers but not the class_definition

# TODO method to parse python code
def parse_python_with_queries():
  parser.set_language(PY_LANGUAGE)
  global tree
  tree = parser.parse(bytes(src_code, "utf8"))


  # query 1: calls all method calls as @method.call and all methods as @function.definition
  query = PY_LANGUAGE.query("""
  (function_definition 
    body: (block
      (expression_statement 
        (call)? @method.call
        (assignment 
          (call)? @method.call)?)?)) @function.definition
  (call) @method.call
  """)
  #print_method_dict_with_queries(query)
  #print('\n')

  # query 2: finds all method calls
  query = PY_LANGUAGE.query("""
  (call) @call
  """)
  print_method_dataframe_with_queries(query)

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

  #print_method_dict_with_queries(query)
  print('\n')
  query = JAVA_LANGUAGE.query("""
  (object_creation_expression) @call

  (method_invocation) @call
  """)
  print_method_dataframe_with_queries(query)

# This is the first version of the query parsing.
# It is given the method and method call nodes and trys to connect them by fitting the start_point of the method.call nodes
# in between the start_point and end_point of a function.definition nodes.  It's not very readable and the one below this is much better
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
    print(call)

# Pre: the start_point and end_point values of a node
# Post: return the substring of the source that the start_point and end_point point to
def get_code_string(start_point, end_point) -> str:
  if start_point[0] == end_point[0]:
    return lines[start_point[0]][start_point[1]:end_point[1]]
  ret = lines[start_point[0]][start_point[1]:]
  ret += "\n".join([line for line in lines[start_point[0] + 1:end_point[0]]])
  ret += "\n" + lines[end_point[0]][:end_point[1]]
  return ret


# This is the second version of query parsing.  It uses the method call nodes to find their corresponding method parent nodes.
# It then pairs them up in a dictionary/dataframe
def print_method_dataframe_with_queries(query):
  captures = query.captures(tree.root_node)     # captures should be a list of every method call in the file based on the query it is based on
  method_dict = {}
  method_defintion = {}
  method_dict['global'] = [[], None]                    # initialize global key for any methods not called from a function
  for capture in captures:
    current_call = capture[0]

    parent = current_call.parent
    function, class_d = None, None
    while parent.parent is not None:            # This loop finds the nearest function and class that the method call is a part of
      if parent.type == 'function_definition' or parent.type == 'method_declaration':
        function = parent
      elif parent.type == 'class_definition' or parent.type == 'class_declaration': 
        class_d = parent
        break
      parent = parent.parent                    # iterate through the method call's parents
      #print(parent) 
    
    call_name = get_code_string(current_call.start_point, current_call.end_point)  # name of the method call
    #print(call_name)

    """if function is None and class_d is None and parent.parent is None:      # method is a global variable
      method_calls = method_dict['global'][0]
      method_calls.append(call_name)
      method_dict['global'][0] = method_calls      # update global method_calls
      continue"""

    if function is not None:
      name_node = function.child_by_field_name('name')    
      parameters_node = function.child_by_field_name('parameters')
      function_name = get_code_string(name_node.start_point, name_node.end_point) + get_code_string(parameters_node.start_point, parameters_node.end_point)
      # Use this if you only want the signature of the function (ex: fuel_up(parameters), main(), ...)
      function_definition = get_code_string(function.start_point, function.end_point)  # Use this if you want the entire function definition (ex: fuel_up(){...})
      method_defintion[function_name] = [function_definition]   # adds function defintion into a dictionary
    else:
      function_name = None
      function_definition = None
    if class_d is not None:                     # This is unused code, but it stores name and defintion of the class closest to the method call
      name_node = class_d.child_by_field_name('name')
      class_name = get_code_string(name_node.start_point, name_node.end_point)
      class_definition = get_code_string(class_d.start_point, class_d.end_point)
    else:
      class_name = None
      class_definition = None

    if function_name in method_dict.keys():         # Since the function is already in the dataframe/dictionary, get the list of method calls, 
      method_calls = method_dict[function_name][0] # append the current method call, and reinitialize the method call list
      method_calls.append(call_name)
      method_dict[function_name][0] = method_calls
    else:                                           # function is not in the dataframe/dictionary, initialize its list of method calls
      method_dict[function_name] = [[call_name], class_name]    # making it a list of lists solve the problem with the lists being of different lengths

      
  df = pd.DataFrame(method_dict)  
  df2 = pd.DataFrame(method_defintion) # creates the method_defintion dict into a dataframe
  print('Function_defintion: ', method_defintion)
  df = pd.concat([df,df2],ignore_index=True)   # concats the defintion to the main dataframe
  columns = list(df)
  for i in columns:
    print(i, df[i][0], df[i][1], df[i][2])

  csv_file = open('test_py.csv', 'w+')  # writes the dataframe to a csv file (this test is for test.py)
  df.to_csv(csv_file)   # csv may be annoying to look at since method defintion takes up a lot of space

  #for call in method_dict.items():
    #print(call)

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