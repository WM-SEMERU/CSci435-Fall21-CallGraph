import sys, os, argparse
import git
from pandas import DataFrame
import build_languages
from LanguageData import LanguageData

method_dict = {
    'method': []
}
method_nodes = []
method_prints = []
file_dict = {}
edge_dict = {
    'callee_index': [],
    'called_index': [],
    'call_line': []
}

src_path = ''

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

def get_method_print(node):
    if lang.language == 'python':
        name = node_to_string(node.child_by_field_name('name'))
        param_node = node.child_by_field_name('parameters')
        if param_node is None:
            nparams = 0
        else:
            params = param_node.children
            nparams = (len(params) - 1) // 2
            for param in params:
                if node_to_string(param) == 'self':
                    nparams -= 1
        parent = node.parent
        parent_class = None
        while parent.type != 'module':
            if parent.type == 'class_definition':
                parent_class = node_to_string(parent.child_by_field_name('name'))
                if name == '__init__':
                    name = parent_class
                break
            parent = parent.parent
    elif lang.language == 'java':
        name = node_to_string(node.child_by_field_name('name'))
        nparams = (len(node.child_by_field_name('parameters').children) - 1) // 2
        parent = node.parent
        parent_class = None
        while parent.type != 'program':
            if parent.type == 'class_declaration':
                parent_class = node_to_string(parent.child_by_field_name('name'))
                break
            parent = parent.parent
    return (name, nparams)

def add_methods_and_imports():
    tree = lang.PARSER.parse(bytes(src_code, "utf8"))
    query = lang.method_import_q
    captures = query.captures(tree.root_node)
    ## adds all the method nodes to a list and all the method definition to a dictionary
    cur_method_nodes = [node[0] for node in captures if node[1] == 'method']

    method_dict['method'].extend([node_to_string(node) for node in cur_method_nodes])
    method_nodes.extend(cur_method_nodes)
    method_prints.extend([get_method_print(node) for node in cur_method_nodes])
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

def get_call_print(node):
    if lang.language == 'python':
        # gets the name of the method call
        func = node.child_by_field_name('function') 
        try:
            name = node_to_string(func) if func.type == 'identifier' else node_to_string(func.child_by_field_name('attribute'))
        except Exception:
            name = None
        if node.child_by_field_name('arguments') is None:
            print(filepath)
            print(node.children)
            print(node_to_string(node))
        # gets the number of arguments passed to the method
        nargs = (len(node.child_by_field_name('arguments').children) - 1) // 2
    elif lang.language == 'java':
        # gets the name of the method call
        if node.type == 'method_invocation':
            name = node_to_string(node.child_by_field_name('name'))
        elif node.type == 'object_creation_expression':
            name = node_to_string(node.child_by_field_name('type'))
        # gets the number of arguments passed to the method
        nargs = (len(node.child_by_field_name('arguments').children) - 1) // 2
    
    return (name, nargs)

def add_edges():
    query = lang.call_q
    method_range = file_dict[filepath][1]
    imports = file_dict[filepath][0]
    for index in range(method_range[0], method_range[1]):
        call_line = -1
        callee_index = index

        node = method_nodes[index]
        calls = [call[0] for call in query.captures(node)]
        for call in calls:
            called_index = -1
            call_line = call.start_point[0] - node.start_point[0]
            call_name = get_call_print(call)
            for file in imports:
                rang = file_dict[file][1]
                for jindex in range(rang[0], rang[1]):
                    method_name = method_prints[jindex]
                    if call_name == method_name:
                        called_index = jindex
                        break
                if called_index != -1:
                    break
            if called_index != -1:
                edge_dict['callee_index'].append(callee_index)
                edge_dict['called_index'].append(called_index)
                edge_dict['call_line'].append(call_line)

def parse_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as file:
            global lines, src_code, filepath
            src_code = file.read()
            lines = src_code.split('\n')
            filepath = path
    except FileNotFoundError:
        exit_with_message('Could not open file: %s' % path)
    

def parse_directory(dir_path):
    src_path = dir_path
    if not os.path.isdir(src_path):
        exit_with_message(f'Could not find directory: {src_path}')
    walk = os.walk(src_path)
    for subdir,dir,files in walk:
        for filename in files:
            path = os.path.join(subdir,filename)
            if filename.endswith(lang.extension):
                parse_file(path)
                add_methods_and_imports()
    for path in file_dict:
        parse_file(path)
        add_edges()

def parse_repo(link):
    repo_name = link.split('/')[-1].replace('.git','')
    path = repo_name
    repo_path = os.path.join(os.path.dirname(__file__), repo_name)
    if not os.path.exists(repo_path):
        try:
            git.Repo.clone_from(link, repo_path)
        except:
            exit_with_message(f"Given repository link {link} does not exist")
    parse_directory(repo_path)

argparser = argparse.ArgumentParser(description='interpret type of parsing')
argparser.add_argument('language')
argparser.add_argument('-f', '--file')
argparser.add_argument('-d', '--directory')
argparser.add_argument('-r', '--repository')
argparser.add_argument('-o', '--output')

def exit_with_message(message):
    print(f"{message} Exiting...")
    sys.exit(1)

def main():
    args = argparser.parse_args(sys.argv[1:])
    directory = os.path.dirname(__file__)
    if not os.path.exists(os.path.join(directory, 'vendor')) or not os.path.exists(os.path.join(directory, 'build')):
        build_languages.main()
    global lang
    lang = LanguageData(args.language)
    global path

    if args.file is not None:
        path = args.file
        parse_file(args.file)
        add_methods_and_imports()
        add_edges()
    elif args.directory is not None:
        path = args.directory
        parse_directory(args.directory)
    elif args.repository is not None:
        path = args.repository
        parse_repo(args.repository)
    else:
        exit_with_message("No File, Directory, or Repository passed as argument.")
    

    method_df = DataFrame(method_dict)
    print(method_df)
    edge_df = DataFrame(edge_dict)
    print(edge_df)
    output = args.output
    if output == None:
        output = os.path.split(path)[1].split('.')[0]
    method_df.to_csv(output + '_method.csv')
    edge_df.to_csv(output + '_edge.csv')
    

if __name__ == '__main__':
    main()
