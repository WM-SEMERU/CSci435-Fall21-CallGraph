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
            call_name = ""
            if lang.language == 'python':
                call_name = node_to_string(call.children[0]) if len(call.children[0].children) == 0 else node_to_string(call.children[0].children[-1]) 
            for file in imports:
                rang = file_dict[file][1]
                for jindex in range(rang[0], rang[1]):
                    method_name = method_dict['method'][jindex]
                    method_name = method_name[:method_name.index('(')].split()[-1]
                    if call_name == method_name:
                        called_index = jindex
                        break
                if called_index != -1:
                    break
            if called_index != -1:
                edge_dict['callee_index'].append(callee_index)
                edge_dict['called_index'].append(called_index)
                edge_dict['call_line'].append(call_line)
            #else:
                #print("Could not find %s call" % call_name)
                """
    tree = lang.PARSER.parse(bytes(src_code, "utf8"))
    query = lang.method_import_q
    captures = query.captures(tree.root_node)
    cur_method_nodes = [node[0] for node in captures if node[1] == 'method']
    query = lang.call_q
    for node in cur_method_nodes:
        captures = query.captures(node)
        call_nodes = [call[0] for call in captures if call[1] == 'call']
        calls = [node_to_string(call) for call in call_nodes]
        parent = node_to_string(node.child_by_field_name('name'))
        edge(calls, parent)

def edge(calls, parent):
    called_index = 0
    for i in range(len(method_dict['method'])):
        method_def = method_dict['method'][i]
        method_name = method_def[:method_def.index('(')].split()[-1].split('.')[-1]
        if parent == method_name:
            called_index = i
            break
    for call in calls:
        line = call
        call = line[:line.index('(')].split()[-1].split('.')[-1]
        for i in range(len(method_dict['method'])):
            method_def = method_dict['method'][i]
            method_name = method_def[:method_def.index('(')].split()[-1].split('.')[-1]
            if call == method_name:
                edge_dict['callee_index'].append(i)
                edge_dict['called_index'].append(called_index)
                edge_dict['call_line'].append(line)"""

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
