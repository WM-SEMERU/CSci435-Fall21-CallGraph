import sys, os, argparse
import git
from pandas import DataFrame
from tree_sitter import Language, Parser
from LanguageData import LanguageData

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

def add_methods_and_imports():
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

def add_edges():
    tree = lang.PARSER.parse(bytes(src_code, "utf8"))
    query = lang.method_import_q
    captures = query.captures(tree.root_node)
    cur_method_nodes = [node[0] for node in captures if node[1] == 'method']
    query = lang.call_q
    for node in cur_method_nodes:
        captures = query.captures(node)
        call_nodes = [call[0] for call in captures if call[1] == 'call']
        calls = [node_to_string(call) for call in call_nodes]
        parent = lines[node.start_point[0]][node.start_point[1]:]
        parent = parent.split('(')[0].split()[-1]
        edge(calls, parent)

def edge(calls, parent):
    called_index = 0
    for i in range(len(method_dict['method'])):
        method = method_dict['method'][i].split()[1]
        method = method.split('(')[0]
        if parent == method:
            called_index = i
            break
    for call in calls:
        line = call
        call = call.split('(')[0]
        if '.' in call:
            call = call.split('.')[1]
        for i in range(len(method_dict['method'])):
            method = method_dict['method'][i].split()[1]
            method = method.split('(')[0]
            if call == method:
                edge_dict['callee_index'].append(i)
                edge_dict['called_index'].append(called_index)
                edge_dict['call_line'].append(line)

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
    global lang
    lang = LanguageData(args.language)
    path = ''

    if args.file is not None:
        parse_file(args.file)
        add_methods_and_imports()
        add_edges()
    elif args.directory is not None:
        path = args.file
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
    if output is not None:
        output = os.path.split(path)[1].split('.')[0]
        DataFrame.from_dict(method_df).to_csv(output + '_method.csv')
        DataFrame.from_dict(edge_df).to_csv(output + '_edge.csv')
    

if __name__ == '__main__':
    main()