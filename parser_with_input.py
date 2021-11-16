import sys, os, argparse
import git
from pandas import DataFrame
from tree_sitter import Language, Parser

class LanguageData:
    def __init__(self, language):
        self.PARSER = Parser()
        if language == 'python' or language == 'py':
            self.language = 'python'
            self.extension = ".py"
            self.language_library = Language('build/my-languages.so', 'python')
            self.PARSER.set_language(self.language_library)
            self.method_import_q = self.language_library.query("""
            (function_definition) @method
            (import_statement) @import
            (import_from_statement) @import
            """)
            self.call_q = self.language_library.query("""
            (call) @call
            (lambda) @lambda
            """)
        elif language == 'java' or language == 'jv':
            self.language = 'java'
            self.extension = ".java"
            self.language_library = Language('build/my-languages.so', 'java') 
            self.PARSER.set_language(self.language_library)
            self.method_import_q = self.language_library.query("""
            (method_declaration) @method
            (constructor_declaration) @method
            (import_declaration) @import 
            """)
            self.call_q = self.language_library.query("""
            (method_invocation) @method
            (object_creation_expression) @method
            """)
        else:
            raise ValueError("Unknown language: %s" % language)

method_dict = {
    'method': []
}
method_nodes = []
file_dict = {}
edge_dict = {
    'callee_index': [],
    'called_index': [],
    'call_line': []
}

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

def add_methods_and_imports(filepath):
    tree = lang.PARSER.parse(bytes(src_code, "utf8"))
    query = lang.method_import_q
    captures = query.captures(tree.root_node)
    ## adds all the method nodes to a list and all the method definition to a dictionary
    cur_method_nodes = [node[0] for node in captures if node[1] == 'method']

    method_dict['method'].extend([node_to_string(node) for node in cur_method_nodes])
    method_nodes.extend(cur_method_nodes)
    ## adds all files that the file imports to a list and the range of indexes in the method dictionary that point to that file
    import_nodes = [node[0] for node in captures if node[1] == 'import']

    file_list = [filepath]
    for imp in import_nodes:
        file_to_search = None
        if lang.language == 'python':
            node = imp.child_by_field_name('name')
            if imp.type == 'import_statement':
                if node.type == 'aliased_import':
                    file_to_search = node_to_string(node.child_by_field_name('name'))
                else:
                    file_to_search = node_to_string(node)
            elif imp.type == 'import_from_statement':
                file_to_search = node_to_string(imp.child_by_field_name('module_name'))
        elif lang.language == 'java':
            for child in imp.children[1:]:
                if child.type == 'identifier' or child.type == 'scoped_identifier':
                    file_to_search = node_to_string(child)
                    break
        import_path = os.path.join(os.path.dirname(filepath), file_to_search.replace(".", os.sep) + lang.extension)
        if os.path.exists(import_path):
            file_list.append(import_path)
    file_dict[filepath] = [file_list, (len(method_nodes) - len(cur_method_nodes), len(method_nodes))]

def add_edges(filepath):
    pass

def parse_file(filepath):
    try:
        file = open(filepath, 'r', encoding='utf-8')
    except FileNotFoundError:
        exit_with_message('Could not open file: %s' % filepath)
    global lines, src_code
    src_code = file.read()
    lines = src_code.split('\n')

def parse_directory(dir_path):
    src_path = dir_path
    if not os.path.isdir(src_path):
        exit_with_message('Could not find directory: %s' % src_path)
    walk = os.walk(src_path)
    for subdir,dir,files in walk:
        for filename in files:
            filepath = os.path.join(subdir,filename)
            if filename.endswith(lang.extension):
                parse_file(filepath)
                add_methods_and_imports(filepath)
    for filepath in file_dict.keys():
        parse_file(filepath)
        add_edges(filepath)

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
    global lang
    lang = LanguageData(args.language)

    if args.file is not None:
        parse_file(args.file)
        add_methods_and_imports(args.file)
        add_edges(args.file)
    elif args.directory is not None:
        parse_directory(args.directory)
    elif args.repository is not None:
        parse_repo(args.repository)
    else:
        exit_with_message("No File, Directory, or Repository passed as argument.")
    
    method_df = DataFrame(method_dict)
    print(method_df)
    edge_df = DataFrame(edge_dict)
    print(edge_df)

if __name__ == '__main__':
    main()