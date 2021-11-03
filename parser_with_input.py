import sys
import os
import pandas as pd
from tree_sitter import Language, Parser

PY_LANGUAGE = Language('build/my-languages.so', 'python')
JAVA_LANGUAGE = Language('build/my-languages.so', 'java') 

parser = Parser()

lang = {
    "python": ["function_definition", "class_definition"],
    "java": ["method_declaration", "class_declaration"]
  }

# TODO method to parse python code
def parse_python_with_queries():
  parser.set_language(PY_LANGUAGE)
  global tree
  tree = parser.parse(bytes(src_code, "utf8"))

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
  (object_creation_expression) @call
  (method_invocation) @call
  """)
  print_method_dataframe_with_queries(query)

# Pre: the start_point and end_point values of a node
# Post: return the substring of the source that the start_point and end_point point to
def get_code_string(start_point, end_point) -> str:
  if start_point[0] == end_point[0]:
    return lines[start_point[0]][start_point[1]:end_point[1]]
  ret = lines[start_point[0]][start_point[1]:] + "\n"
  ret += "\n".join([line for line in lines[start_point[0] + 1:end_point[0]]])
  ret += "\n" + lines[end_point[0]][:end_point[1]]
  return ret


# This method uses the method call nodes to find their corresponding method parent nodes.
# It then pairs them up in a dictionary/dataframe
def print_method_dataframe_with_queries(query):
  captures = query.captures(tree.root_node)     # captures should be a list of every method call in the file based on the query it is based on
  method_dict = {}
  method_dict['null'] = [[], 'null', 'null']
  for capture in captures:
    current_call = capture[0]

    parent = current_call.parent
    function, class_d = None, None
    while parent.parent is not None:            # This loop finds the nearest function and class that the method call is a part of
      if parent.type == lang[key][0]:
        function = parent
      elif parent.type == lang[key][1]: 
        class_d = parent
        break
      parent = parent.parent                    # iterate through the method call's parents
    
    call_name = get_code_string(current_call.start_point, current_call.end_point)  # name of the method call

    if parent.parent is None and function is None and class_d is None:                   # method is a global variable
      method_calls = method_dict['null'][0]
      method_calls.append(call_name)
      method_dict['null'][0] = method_calls      # update global method_calls
      continue

    if function is not None:
      name_node = function.child_by_field_name('name')    
      parameters_node = function.child_by_field_name('parameters')
      function_name = get_code_string(name_node.start_point, name_node.end_point) + get_code_string(parameters_node.start_point, parameters_node.end_point)
      function_definition = get_code_string(function.start_point, function.end_point)
    else:
      function_name = 'null'
      function_definition = 'null'
    if class_d is not None:
      name_node = class_d.child_by_field_name('name')
      class_name = get_code_string(name_node.start_point, name_node.end_point)
      class_definition = get_code_string(class_d.start_point, class_d.end_point)
    else:
      class_name = 'null'
      class_definition = 'null'

    if function_name in method_dict.keys():         # Since the function is already in the dataframe/dictionary, get the list of method calls, 
      method_calls = method_dict[function_name][0] # append the current method call, and reinitialize the method call list
      method_calls.append(call_name)
      method_dict[function_name][0] = method_calls
    else:                                           # function is not in the dataframe/dictionary, initialize its list of method calls
      method_dict[function_name] = [[call_name], class_name, function_definition]    # making it a list of lists solve the problem with the lists being of different lengths


  df = pd.DataFrame(method_dict)  

  print(df.to_csv(sep = '\n'))   # csv may be annoying to look at since method defintion takes up a lot of space

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
  
  global key
  if ".py" in filepath:
    key = "python"
    parse_python_with_queries()
  elif ".java" in filepath:
    key = "java"
    parse_java_with_queries()


if __name__ == '__main__':
  main()