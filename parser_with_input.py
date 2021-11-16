import sys, os, argparse
import git
from pandas import DataFrame
# from tree_sitter import Language, Parser
import Language

# PY_LANGUAGE = Language('build/my-languages.so', 'python')
# JAVA_LANGUAGE = Language('build/my-languages.so', 'java') 

# parser = Parser()

# lang = {
#     "python": ["function_definition", "class_definition"],
#     "java": ["method_declaration", "class_declaration"]
#     }
# extensions = ['.py', '.java']

method_df = {
    'method': []
}
edge_df = {
    'callee_index': [],
    'called_index': [],
    'call_index': []
}

src_path = ''

# # file dictionary:
# # key = filepath (so we can quickly open it)
# # values:
# # - the filepaths of the files it imports from the directory
# # - the start index of its methods in the methods csv
# # - the end index of its methods in the methods csv
# def parse_python():
#     parser.set_language(PY_LANGUAGE)
#     global tree
#     tree = parser.parse(bytes(src_code, "utf8"))

#     query = PY_LANGUAGE.query("""
#     (function_definition) @method
#     (import_statement) @import
#     (import_from_statement) @import_from
#     """)
#     captures = query.captures(tree.root_node)
#     method_nodes = [node[0] for node in captures if node[1] == 'method']
#     import_nodes = [node[0] for node in captures if node[1] == 'import' or node[1] == 'import_from']
#     method_df['methods'].extend([node_to_string(node) for node in method_nodes])

#     imports = []
#     for imp in import_nodes:
#         file_to_search, name_to_search, thing_to_search = None, None, None
#         if imp.type == 'import_statement':
#             node = imp.child_by_field_name('name')
#             if node.type == 'aliased_import':
#                 file_to_search = node_to_string(node.child_by_field_name('name'))
#                 name_to_search = node_to_string(node.child_by_field_name('alias'))
#             else:
#                 file_to_search = node_to_string(node)
#         elif imp.type == 'import_from_statement':
#             file_to_search = node_to_string(imp.child_by_field_name('module_name'))
#             node = imp.child_by_field_name('name')
#             if node.type == 'aliased_import':
#                 thing_to_search = node_to_string(node.child_by_field_name('name'))
#                 name_to_search = node_to_string(node.child_by_field_name('alias'))
#             else:
#                 thing_to_search = node_to_string(node)
#         imports.append(tuple([file_to_search.replace('.',os.sep), thing_to_search, name_to_search]))

#     query = PY_LANGUAGE.query("""
#     (call) @call
#     (lambda) @lambda
#     """)
#     for node in method_nodes:
#         captures = query.captures(node)
#         call_nodes = [call[0] for call in captures if call[1] == 'call']
#         calls = [node_to_string(call) for call in call_nodes]



# def parse_java():
#     parser.set_language(JAVA_LANGUAGE)
#     global tree
#     tree = parser.parse(bytes(src_code, "utf8"))

#     query = JAVA_LANGUAGE.query("""
#     (method_declaration) @method
#     (import_declaration) @import
#     """)
#     captures = query.captures(tree.root_node)
#     method_nodes = [node[0] for node in captures if node[1] == 'method']
#     import_nodes = [node[0] for node in captures if node[1] == 'import']
#     method_df['methods'].extend([node_to_string(node) for node in method_nodes])
#     imports = []
#     for imp in import_nodes:
#         for child in imp.children[1:]:
#             if child.type == 'identifier' or child.type == 'scoped_identifier':
#                 ident_str = node_to_string(child)
#                 break
#         imports.append(ident_str.replace(".", os.sep))


# Pre: the start_point and end_point values of a node
# Post: return the substring of the source that the start_point and end_point point to
def node_to_string(node) -> str:
    start_point = node.start_point
    end_point = node.end_point
    if start_point[0] == end_point[0]:
        return lines[start_point[0]][start_point[1]:end_point[1]]
    ret = lines[start_point[0]][start_point[1]:] + "\n"
    ret += "\n".join([line for line in lines[start_point[0] + 1:end_point[0]]])
    ret += "\n" + lines[end_point[0]][:end_point[1]]
    return ret

def parse_file(filepath):
    global lines, src_code, key
    src_path = filepath

    try:
        file = open(src_path, 'r', encoding='utf-8')
    except FileNotFoundError:
        exit_with_message('Could not open file: %s' % src_path)

    src_code = file.read()
    lines = src_code.split('\n')
    if filepath.endswith(".py"):
        key = 'python'
        language = Language("python")
    elif filepath.endswith(".java"):
        key = 'java'
        language = Language("java")
    
    method_nodes = []
    import_nodes = []
    language.parse(src_code, method_nodes, import_nodes)

def parse_directory(dir_path):
    src_path = dir_path
    if not os.path.isdir(src_path):
        exit_with_message('Could not find directory: %s' % src_path)
    for subdir,dir,files in os.walk(src_path):
        for filename in files:
            filepath = os.path.join(subdir,filename)
            if filename.endswith('.py'):
                parse_file(filepath)
            elif filename.endswith('.java'):
                parse_file(filepath)

def parse_repo(link):
    repo_name = link.split('/')[-1].replace('.git','')
    repo_path = os.path.join(os.path.dirname(__file__), repo_name)
    if not os.path.exists(repo_path):
        try:
            git.Repo.clone_from(link, repo_path)
        except:
            exit_with_message("Given repository link'%s' does not exist", link)
    parse_directory(repo_path)

argparser = argparse.ArgumentParser(description='interpret type of parsing')
argparser.add_argument('language')
argparser.add_argument('-f', '--file')
argparser.add_argument('-d', '--directory')
argparser.add_argument('-r', '--repository')

def exit_with_message(message):
    print(message)
    print("Exiting...")
    sys.exit(1)

def main():
    args = argparser.parse_args(sys.argv[1:])
    print(args)
    
    if args.language == 'python' or args.language == 'py':
        pass
    elif args.language == 'java' or args.language == 'jv':
        pass
    else:
        exit_with_message("No language specified or the language is not supported. Exiting...")

    if args.file is not None:
        parse_file(args.file)
    elif args.directory is not None:
        parse_directory(args.directory)
    elif args.repository is not None:
        parse_repo(args.repository)
    else:
        exit_with_message("No File, Directory, or Repository passed as argument.")
    
    print(method_df)
    print(edge_df)

if __name__ == '__main__':
    main()