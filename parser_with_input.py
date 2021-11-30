import sys, os, argparse
import git
from pandas import DataFrame
import build_languages
from parsers.python_parser import PythonParser
from parsers.java_parser import JavaParser

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

def add_methods_and_imports():
    tree = lang.PARSER.parse(bytes(lang.src_code, "utf8"))
    query = lang.method_import_q
    captures = query.captures(tree.root_node)
    ## adds all the method nodes to a list and all the method definition to a dictionary
    cur_method_nodes = [node[0] for node in captures if node[1] == 'method']

    method_dict['method'].extend([lang.node_to_string(node) for node in cur_method_nodes])
    method_nodes.extend(cur_method_nodes)
    method_prints.extend([lang.get_method_print(node) for node in cur_method_nodes])
    ## adds all files that the file imports to a list and the range of indexes in the method dictionary that point to that file
    import_nodes = [node[0] for node in captures if node[1] == 'import']

    file_list = [lang.filepath]
    for imp in import_nodes:
        file_to_search = lang.get_import_file(imp)
        import_path = os.path.join(os.path.dirname(lang.filepath), file_to_search.replace(".", os.sep) + lang.extension)
        if os.path.exists(import_path):
            file_list.append(import_path)
    file_dict[lang.filepath] = [file_list, (len(method_nodes) - len(cur_method_nodes), len(method_nodes))]

def add_edges():
    query = lang.call_q
    method_range = file_dict[lang.filepath][1]
    imports = file_dict[lang.filepath][0]
    for index in range(method_range[0], method_range[1]):
        call_line = -1
        callee_index = index

        node = method_nodes[index]
        calls = [call[0] for call in query.captures(node)]
        for call in calls:
            called_index = -1
            call_line = call.start_point[0] - node.start_point[0]
            call_name = lang.get_call_print(call)
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

def parse_directory(dir_path):
    src_path = dir_path
    if not os.path.isdir(src_path):
        exit_with_message(f'Could not find directory: {src_path}')
    walk = os.walk(src_path)
    for subdir,dir,files in walk:
        for filename in files:
            path = os.path.join(subdir,filename)
            if filename.endswith(lang.extension):
                lang.set_current_file(path)
                add_methods_and_imports()
    for path in file_dict:
        lang.set_current_file(path)
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
    if args.language == 'python':
        lang = PythonParser()
    elif args.language == 'java':
        lang = JavaParser()
    global path

    if args.file is not None:
        path = args.file
        lang.set_current_file(args.file)
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
