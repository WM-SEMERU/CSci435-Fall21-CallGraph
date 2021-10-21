import re
import sys

output_file = sys.argv[2]
test_file = sys.argv[1]
function = 'call'
function2 = 'function'
function2_2 = 'definition'
if '.java' in test_file:
	function = 'invocation'
	function2 = 'method'
	function2_2 = 'declaration'
code_lines = []
with open(test_file, 'r') as test:
    code_lines = [line.split('\n') for line in test]

with open(output_file, 'r') as tree:
    # Turns output.py into a 2D array organized by line
    lines = [line.split() for line in tree]

    #adding comment
    # These are the character that are to be removed
    replace_letters = ['[',']','-','(',')']
    
    # iterate through the 2D array of the output
    # remove any characters that are not letters, underscores, or numbers
    # returns same thing but cleaned up
    new_lines = []
    for i in lines:
        temp = re.sub('[^A-Za-z0-9]', ' ', str(i))
        new_lines.append(temp)

    calls = []
    calls2 = {}
    lastKey = ''
    for i in new_lines:
        i = i.split()
        for n in range(len(i)):
            if i[n].find(function) != -1:
                calls2[lastKey].append(code_lines[int(i[n + 1])][0][int(i[n + 2]):int(i[n + 4])])
                calls.append([code_lines[int(i[n + 1])][0][int(i[n + 2]):int(i[n + 4])], i])
                break
            if i[n].find(function2) != -1 and i[n+1].find(function2_2) != -1:
                calls2[code_lines[int(i[n + 2])][0]] = []
                lastKey = code_lines[int(i[n + 2])][0]
                break

    
    # print statements

    #print(new_lines)     
    #print(lines)
    #print(len(lines[10]))
    for line in calls2:
        print(line)
        print(calls2[line])

    # for line in code_lines:
    #     print(line)




