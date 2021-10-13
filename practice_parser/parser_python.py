# TODO write a method such that:
#       input: tree-sitter output
#       output: 2D array with only letters, numbers, underscores


import re

# output.py is the tree-sitter output for test.py
with open('output_py.txt', 'r') as tree:
    # Turns output.py into a 2D array organized by line
    lines = [line.split() for line in tree]

    # These are the character that are to be removed
    replace_letters = ['[',']','-','(',')']
    
    # iterate through the 2D array of the output
    # remove any characters that are not letters, underscores, or numbers
    # returns same thing but cleaned up
    new_lines = []
    for i in lines:
        temp = re.sub('[^A-Za-z0-9]', '', str(i))
        new_lines.append(temp)

    
    # print statements

    #print(new_lines)     
    #print(lines)
    print(len(lines[10]))
    print(lines[10])

