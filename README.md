# CSci435-Fall21-CallGraph

## Background
Graphs are a great way of representing complex relationships in all types of data. Graph Neural Networks (GNNs) have seen a lot of interest in research and industry for capturing these complex relationships to perform tasks such as node classification, link prediction, and embedding generation for search. Some work has been done to represent source code as graphs and apply GNNs to them. However, they don’t go beyond method level as they usually only focus on the Abstract Syntax Tree (AST) of a method. Going beyond method level can help model more complex software systems for performing more interesting tasks. Luckily software systems can be represented in multiple ways using graphs such as UML diagrams, ASTs and Call Graphs, allowing these GNNs to be applied to entire software systems.

## Project Goal
There are plenty of tools available for generating these Call Graphs for software systems. However, they are disconnected from each other, one only working on Java, one only generating XML format working in another language. Others only allow for using a GUI to operate making it difficult to use at scale. The main vision of this project is to create a tool that can generate Call Graphs of different software systems, regardless of language, in a format that can easily be used by current GNNs. This tool should be easy to use and extend allowing for researchers to easily use them for training these GNNs. Your mission, should you choose to accept it, will be to build this tool and if time permits to test it on some GNN models!

# Installation

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
    cd vendor
```

Then clone the grammar's for Python and Java using:
```
    git clone https://github.com/tree-sitter/tree-sitter-python.git
    git clone https://github.com/tree-sitter/tree-sitter-java.git
```

# Executing the code

The the code can be executed using:
```
    python parser_with_input.py test.py > test.csv
```
Where ```test.py``` is the python or java file you want a call graph for. The call graph is then saved as ```test.csv```

## Resources

- [Tree-Sitter Programming Language Parser](https://github.com/tree-sitter/tree-sitter)
- [srcML](https://www.srcml.org/#home)
- [Call Graph](https://youtu.be/4ChfDsBEm_A)
- [Graph Neural Networks](https://youtu.be/me3UsMm9QEs)

## Existing Tools

- [Java CallGraph](https://github.com/gousiosg/java-callgraph)
