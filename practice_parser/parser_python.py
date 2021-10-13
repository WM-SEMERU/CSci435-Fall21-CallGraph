import re

lines = []



with open('test.py','r') as f, open('output.txt', 'r') as tree:
    # tree = tree.readlines()
    new_lines = []
    lines = [line.split() for line in tree]
    replace_letters = ['[',']','-']
    
    for i in lines:
        temp = re.sub('[^A-Za-z0-9]', '', str(i))
        new_lines.append(temp)
    #print(new_lines)     
    #print(lines)
    print(len(lines[10]))
    print(lines[10])

