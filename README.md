# CSci435-Fall21-CallGraph

## Background
Graphs are a great way of representing complex relationships in all types of data. Graph Neural Networks (GNNs) have seen a lot of interest in research and industry for capturing these complex relationships to perform tasks such as node classification, link prediction, and embedding generation for search. Some work has been done to represent source code as graphs and apply GNNs to them. However, they don’t go beyond method level as they usually only focus on the Abstract Syntax Tree (AST) of a method. Going beyond method level can help model more complex software systems for performing more interesting tasks. Luckily software systems can be represented in multiple ways using graphs such as UML diagrams, ASTs and Call Graphs, allowing these GNNs to be applied to entire software systems.

## Project Goal
There are plenty of tools available for generating these Call Graphs for software systems. However, they are disconnected from each other, one only working on Java, one only generating XML format working in another language. Others only allow for using a GUI to operate making it difficult to use at scale. The main vision of this project is to create a tool that can generate Call Graphs of different software systems, regardless of language, in a format that can easily be used by current GNNs. This tool should be easy to use and extend allowing for researchers to easily use them for training these GNNs. Your mission, should you choose to accept it, will be to build this tool and if time permits to test it on some GNN models!

# Installation

First, clone our repository onto your local machine using:
```bash
    git clone git@github.com:WM-SEMERU/CSci435-Fall21-CallGraph.git
```

Then, make sure you have the latest version of tree-sitter's python library installed using:
```bash
    pip install -r requirements.txt
```

Our current working version will creeate call graphs for Python and Java files, directories, and git repositories. So, for tree-sitter to parse the code you will need the grammars' for both Python and Java installed in the ```vendor``` folder.
This can be done by running the build_languages.py file with the following command:
```bash
    python build_languages.py
```
This will create the ```build/``` directory and the ```my-languages.so``` file that tree-sitter uses to parse the languages.

# Executing the code
The program supports multiple flags for files, directories, and repositories. Use the ```-f``` or ```--file``` flags to parse a file. Use ```-d``` or ```--directory``` to parse a directory. Use the ```-r``` or ```--repository``` to parse a git repository. The ```-o``` or ```--output``` to name the output of the csv files. Make sure to tell the program which language you're parsing. 

## Parsing a file
```bash
    python parser_with_input.py python -f test.py
```
Where ```test.py``` is the python or java file you want a call graph for. The call graph is then saved as ```test_method.csv``` and ```test_edge.csv```.

## Parsing a directory
```bash
    python parser_with_input.py java -d /path/to/java/project -o java-graph
```
Where ```/path/to/java/project``` is the python or java project directory you want a call graph for. The call graph is then saved as ```java-graph_method.csv``` and ```java-graph_edge.csv```.

## Parsing a repository
```bash
    python parser_with_input.py java -r https://github.com/username/project.git -o project
```
Where ```https://github.com/username/project.git``` is the python or java project repository you want a call graph for. The call graph is then saved as ```project_method.csv``` and ```project_edge.csv```.

## Resources

- [Tree-Sitter Programming Language Parser](https://github.com/tree-sitter/tree-sitter)
- [srcML](https://www.srcml.org/#home)
- [Call Graph](https://youtu.be/4ChfDsBEm_A)
- [Graph Neural Networks](https://youtu.be/me3UsMm9QEs)

## Existing Tools

- [Java CallGraph](https://github.com/gousiosg/java-callgraph)
