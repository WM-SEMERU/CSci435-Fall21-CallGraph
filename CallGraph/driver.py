import sys, os, argparse
import build_languages
import graph_generator

argparser = argparse.ArgumentParser(description='interpret type of parsing')
argparser.add_argument('language')
argparser.add_argument('-f', '--file')
argparser.add_argument('-d', '--directory')
argparser.add_argument('-r', '--repository')
argparser.add_argument('-o', '--output')

def main(argv):
    args = argparser.parse_args(argv)
    directory = os.path.dirname(__file__)
    if not os.path.exists(os.path.join(directory, 'vendor')) or not os.path.exists(os.path.join(directory, 'build')):
        build_languages.main()

    graph_generator.set_language(args.language)
    
    method_df, edge_df = None, None
    if args.file is not None:
        path = args.file
        method_df, edge_df = graph_generator.parse_file(args.file)
    elif args.directory is not None:
        path = args.directory
        method_df, edge_df = graph_generator.parse_directory(args.directory)
    elif args.repository is not None:
        path = args.repository
        method_df, edge_df = graph_generator.parse_repo(args.repository)
    else:
        print("No File, Directory, or Repository passed as argument. Exiting...")
        exit(1)
    
    output = args.output
    if output == None:
        output = os.path.split(path)[1].split('.')[0]
    if not os.path.exists("output"):
        os.mkdir("output")
    method_df.to_csv("output" + os.sep + "" + output + '_method.csv')
    edge_df.to_csv("output" + os.sep + "" + output + '_edge.csv')
    

if __name__ == '__main__':
    main(sys.argv[1:])
