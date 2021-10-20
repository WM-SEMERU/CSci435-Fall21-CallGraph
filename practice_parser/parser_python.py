# TODO write a method such that:
#       input: tree-sitter output
#       output: 2D array with only letters, numbers, underscores

import sys
import re

output_file = sys.argv[2]
test_file = sys.argv[1]
function = 'call'
if '.java' in test_file:
    function = 'invocation'

# output.py is the tree-sitter output for test.py
code_lines = []
with open(test_file, 'r') as test:
    code_lines = [line.split('\n') for line in test] 

with open(output_file, 'r') as tree:
    # Turns output.py into a 2D array organized by line
    lines = [line.split() for line in tree]

    # These are the character that are to be removed
    replace_letters = ['[',']','-','(',')']
    
    # iterate through the 2D array of the output
    # remove any characters that are not letters, underscores, or numbers
    # returns same thing but cleaned up
    new_lines = []
    calls = []
    for i in lines:
        temp = re.sub('[^A-Za-z0-9]', ' ', str(i))
        new_lines.append(temp)
    for i in new_lines:
        i = i.split()
        for n in range(len(i)):
            if i[n].find(function) != -1:
                calls.append(code_lines[int(i[n+1])][0][int(i[n+2]):int(i[n+4])])
                break
    
    # print statements

    #print(new_lines)     
    #print(lines)
    #print(len(lines[10]))
    #print(lines[10])
    print(calls)

