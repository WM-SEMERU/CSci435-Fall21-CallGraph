import sys
import re

class Parser:

    # determines function type
    # returnes codelines
    def codelines(self, test_file):
        if '.java' in test_file:
            function = 'invocation'
        elif '.py' in test_file:
            function = 'call'
        # code_lines is an array where each element is a line of code
        code_lines = []
        with open(test_file, 'r') as test:
            code_lines = [line.split('\n') for line in test] # this assumes method calls are oneline
        return code_lines, function

    # returns method calls from the output file
    def getCalls(self, output_file, code_lines, function):
        with open(output_file, 'r') as tree:
            # Turns output.py into a 2D array organized by line
            lines = [line.split() for line in tree]

            # An array with only tree-sitter identifiers and their code location indexes
            new_lines = []
            for line in lines:
                new_lines.append(re.sub('[^A-Za-z0-9]', ' ', str(line)))

            # final array containing the method calls
            calls = []
            for i in new_lines:
                node = i.split()
                for n in range(len(node)):
                    if node[n].find(function) != -1: # true if the node contains a function call
                        # appends corresponding call to the output array with indexes as integers
                        calls.append(code_lines[int(node[n+1])][0][int(node[n+2]):int(node[n+4])]) 
                        break
            return calls


def main():
    parser = Parser()
    output_file = sys.argv[2]
    test_file = sys.argv[1]
    
    code_lines, function = parser.codelines(test_file)
    print(parser.getCalls(output_file, code_lines, function))

if __name__ == '__main__':
    main()