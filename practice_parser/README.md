# Instilation

First, clone our repository onto your local machine using:
```
    git clone git@github.com:WM-SEMERU/CSci435-Fall21-CallGraph.git
```

Then, make sure you have the latest version of tree-sitter's python library installed using:
```
    pip install tree-sitter
```

Our current working version will creeate call graphs for singular Python and Java files. So, for tree-sitter to parse the code you will need the grammars' for both Python and Java installed in the ```vendor``` folder.
in the repository's folder navigate to the ```vendor``` folder:
```
    cd practice_parser/vendor
```

Then clone the grammar's for Python and Java using:
```
    git clone https://github.com/tree-sitter/tree-sitter-python.git
    git clone https://github.com/tree-sitter/tree-sitter-java.git
```

# Executing the code

Navigate to the ```practice_parser``` folder in the repository:
```
    cd practice_parser
```

The the code can be executed using:
```
    python parser_with_input.py test.py
```
Where ```test.py``` is the python or java file you want a call graph for. The call graph is then saved in the folder as ```test_py.csv```.