import os, git
from pandas import DataFrame
import parsers

def reset_graph():
    global method_dict, file_dict, edge_dict
    method_dict = {
        'method': [],
        'nodes': [],
        'prints': []
    }
    file_dict = {}
    edge_dict = {
        'callee_index': [],
        'called_index': [],
        'call_line': []
    }

def add_methods_and_imports():
    tree = lang.PARSER.parse(bytes(lang.src_code, "utf8"))
    query = lang.method_import_q
    captures = query.captures(tree.root_node)
    ## adds all the method nodes to a list and all the method definition to a dictionary
    cur_method_nodes = [node[0] for node in captures if node[1] == 'method']

    method_dict['method'].extend([lang.node_to_string(node) for node in cur_method_nodes])
    method_dict['nodes'].extend(cur_method_nodes)
    method_dict['prints'].extend([lang.get_method_print(node) for node in cur_method_nodes])
    ## adds all files that the file imports to a list and the range of indexes in the method dictionary that point to that file
    import_nodes = [node[0] for node in captures if node[1] == 'import']

    file_list = [lang.filepath]
    for imp in import_nodes:
        file_to_search = lang.get_import_file(imp)
        import_path = os.path.join(os.path.dirname(lang.filepath), file_to_search)
        if os.path.exists(import_path):
            file_list.append(import_path)
    file_dict[lang.filepath] = [file_list, (len(method_dict['nodes']) - len(cur_method_nodes), len(method_dict['nodes']))]

def add_edges():
    query = lang.call_q
    method_range = file_dict[lang.filepath][1]
    imports = file_dict[lang.filepath][0]
    for index in range(method_range[0], method_range[1]):
        call_line = -1
        callee_index = index
        node = method_dict['nodes'][index]
        calls = [call[0] for call in query.captures(node)]
        for call in calls:
            called_index = -1
            call_line = call.start_point[0] - node.start_point[0]
            call_name = lang.get_call_print(call)
            for file in imports:
                rang = file_dict[file][1]
                for jindex in range(rang[0], rang[1]):
                    method_name = method_dict['prints'][jindex]
                    if call_name == method_name:
                        called_index = jindex
                        break
                if called_index != -1:
                    break
            if called_index != -1:
                edge_dict['callee_index'].append(callee_index)
                edge_dict['called_index'].append(called_index)
                edge_dict['call_line'].append(call_line)


def set_language(language):
    global lang
    if language == 'python':
        lang = parsers.PythonParser()
    elif language == 'java':
        lang = parsers.JavaParser()
    elif language == 'cpp':
        lang = parsers.CppParser()

def parse_file(path) -> DataFrame:
    reset_graph()
    try:
        if lang is None:
            pass
    except NameError:
        exit_with_message("No language specified")
    lang.set_current_file(path)
    add_methods_and_imports()
    add_edges()
    return DataFrame({'method': method_dict['method']}), DataFrame(edge_dict)
    

def parse_directory(dir_path) -> DataFrame:
    reset_graph()
    try:
        if lang is None:
            pass
    except NameError:
        exit_with_message("No language specified")
    if not os.path.isdir(dir_path):
        exit_with_message(f'Could not find directory: {dir_path}')
    walk = os.walk(dir_path)
    for subdir,_,files in walk:
        for filename in files:
            path = os.path.join(subdir,filename)
            if filename.endswith(lang.extension):
                lang.set_current_file(path)
                add_methods_and_imports()
    for path in file_dict:
        lang.set_current_file(path)
        add_edges()
    return DataFrame({'method': method_dict['method']}), DataFrame(edge_dict)

def parse_repo(link) -> DataFrame:
    try:
        if lang is None:
            pass
    except NameError:
        exit_with_message("No language specified")
    repo_name = link.split('/')[-1].replace('.git','')
    repo_path = os.path.join(os.path.dirname(__file__), repo_name)
    if not os.path.exists(repo_path):
        try:
            git.Repo.clone_from(link, repo_path)
        except Exception:
            exit_with_message(f"Given repository link {link} does not exist")
    with open(".gitignore", "a") as f:
        f.write(repo_path)
    return parse_directory(repo_path)

def exit_with_message(message):
    print(f"{message} Exiting...")
    exit(1)
