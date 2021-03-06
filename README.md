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
    python driver.py python -f test.py
```
Where ```test.py``` is the python or java file you want a call graph for. The call graph is then saved as ```test_method.csv``` and ```test_edge.csv```.

## Parsing a directory
```bash
    python driver.py java -d /path/to/java/project -o java-graph
```
Where ```/path/to/java/project``` is the python or java project directory you want a call graph for. The call graph is then saved as ```java-graph_method.csv``` and ```java-graph_edge.csv```.

## Parsing a repository
```bash
    python driver.py java -r https://github.com/username/project.git -o project
```
Where ```https://github.com/username/project.git``` is the python or java project repository you want a call graph for. The call graph is then saved as ```project_method.csv``` and ```project_edge.csv```.

# Adding New Languages
We have made our generator modulular so anyone, with a little effort can extned our work to support more languages. Visit the [tree-sitter documantation](https://tree-sitter.github.io/tree-sitter/#available-parsers) to view which languaages are available to parse. From that page navigate to the github of the grammar for the language you wish to add.

## Build the new language
Start by adding the new language to build_languages.py
```python
    def main():
        path = os.path.dirname(__file__)
        folder_path = os.path.join(path, "vendor")
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        repository_path = os.path.join(folder_path, "tree-sitter-python")
        if not os.path.exists(repository_path):
            git.Repo.clone_from("https://github.com/tree-sitter/tree-sitter-python", repository_path)
        repository_path = os.path.join(folder_path,"tree-sitter-java")
        if not os.path.exists(repository_path):
            git.Repo.clone_from("https://github.com/tree-sitter/tree-sitter-java", repository_path)
        repository_path = os.path.join(folder_path,"tree-sitter-cpp")
        if not os.path.exists(repository_path):
            git.Repo.clone_from("https://github.com/tree-sitter/tree-sitter-cpp", repository_path)
        
        Language.build_library(
        'build/my-languages.so',
        [
            'vendor/tree-sitter-python',
            'vendor/tree-sitter-java',
            'vendor/tree-sitter-cpp'
        ]
        )
```

To clone the new language grammar add the following lines after the final ```if not``` statement and replace the github link with the one to the new grammar and the folder path to match the name of the repository. For example the following code would clone the C# grammar.
```python
        repository_path = os.path.join(folder_path,"tree-sitter-c-sharp")
        if not os.path.exists(repository_path):
            git.Repo.clone_from("https://github.com/tree-sitter/tree-sitter-c-sharp", repository_path
```

Finally add the path to the newly cloned grammar to the build_library command.
```python
    Language.build_library(
        'build/my-languages.so',
        [
            'vendor/tree-sitter-python',
            'vendor/tree-sitter-java',
            'vendor/tree-sitter-cpp',
            'vendor/tree-sitter-c-sharp'
        ]
        )
```

## Create Language Parser Class
The ```parsers``` folder holds our language parser classes, which is responsible for holding all the language specific information. To add the new language create a new class and extend the CallParser class, located in the call_parser.py file. Each class must have fields to hold the language name, file extension, tree-sitter Language object, method_and_import query, and the call query. Queries are a way of interfacing with the tree-sitter library to grab all the instances of a certian tag in a given code block. For the method_and_import query. You need to find out what the languages calls its method definitions (it may treat constructors differently, see java for an example) and import statements and attach them to the method and import tags respectively. Likewise for the call queries you need to find out what the language calls method calls and if it treats constructor calls differently. To get this information you can paste an example file into the [tree-sitter playground](https://tree-sitter.github.io/tree-sitter/playground). For more information on queries, look at the [tree-sitter documentaion](https://tree-sitter.github.io/tree-sitter/using-parsers#query-syntax). The CallParser class has a few abstract methods that you will need to create and implement ```get_call_print(self, call)``` and ```get_method_print(self, method)```. You can view the comments in the call_parser.py to get more information on how to implement these methods. Note that depending on how the language handles imports you will need to override the ```get_import_file``` function (see cpp_parser.py). 

## Add The New Class to graph_generator.py
Finally, in the ```graph_generator.py``` file, add the language to the ```set_language``` method.
```python
    def set_language(language):
        global lang
        if language == 'python':
            lang = parsers.PythonParser()
        elif language == 'java':
            lang = parsers.JavaParser()
        elif language == 'cpp':
            lang = parsers.CppParser()
        elif language == 'c_sharp':
            lang = parsers.C_sharpParser()
```
Now you can call the program as you would with any other language using the string you defined in the elif statement.

# CSV Output Format
Two csv files are outputted after parsing a file, directory, or repository. The first file with the ```_method.csv``` suffix matches each method declaration with an index. 
```
	method
0	"def __init__(self, brand, model, type):
        self.brand = brand
        self.model = model
        self.type = type
        self.gas_tank_size = 14
        self.fuel_level = 0"
1	"def fuel_up(self):
        self.fuel_level = self.gas_tank_size
        print('Gas tank is now full.')
        self.read_to_drive()"
...
```
The second file with the ```_edge.csv``` suffix has three columns. The first is callee_index, which contains the indices of the methods (found in the method.csv) that are making the calls. The second column, called_index, contains the indices of the methods that are being called. The third column, call_line, gives the line numbers where the called_index methods are called inside of the callee_index methods.

```
	callee_index	called_index	call_line
0	    1	               3	         3
1	    3	               2	         2
...
```

# Running the Test Cases 
There are a number of test cases one can run to make sure that the CSV files have the desired call graphs. Moreover, you may add two additional files to test the output CSV against your expected CSV files line-by-line. In other words, if you have an idea of what the call graph should look like, you can use this as a method of comparing the output. 

To run the test cases, use the following command: 
```bash
    python unit_test.py output_method.csv output_edge.csv
```

where ```unit_test.py``` is the unit test file, ```output_method.csv``` is the method CSV after parsing the file, and ```output_edge.csv``` is the edge CSV after parsing the file. 

If you have CSV files that you would like to test line-by-line, then you may also run the test cases in the following manner:

```bash
    python unit_test.py output_method.csv output_edge.csv expected_method.csv expected_edge.csv
```

where ```expected_method.csv``` and ```expected_edge.csv``` are the method and edge CSVs, respectively, that you would like to compare with the output. 

## Uploading to test PyPI
In order to upload the project to test PyPI, make sure you have the setuptools, wheel, and twine pip packages installed and up-to-date with these commands:

To install the packages:
```bash
    pip install setuptools wheel twine
```

To update the packages:
```bash
    pip install -U setuptools wheel twine
```

Once this is done, create a source distribution of the project
```bash 
    python setup.py sdist
```

This command should create a folder named dist in the directory with a file in it named ```CallGraph-<verion_number>.tar.gz```.
After this, create a wheel distribution as well:
```bash
    python setup.py bdist_wheel --universal
```

This should add an additional file to the ```dist``` folder ending in the ```.whl``` file extension.
With these two files created, upload the distributions to test PyPI with the following command:
```bash
    twine upload --repository testpypi dist/*
```

To check if the project uploaded, go to the [TestPyPI website](https://test.pypi.org/) and search for CallGraph. You should find a recently uploaded one there.
## Resources

- [Tree-Sitter Programming Language Parser](https://github.com/tree-sitter/tree-sitter)
- [srcML](https://www.srcml.org/#home)
- [Call Graph](https://youtu.be/4ChfDsBEm_A)
- [Graph Neural Networks](https://youtu.be/me3UsMm9QEs)

## Existing Tools

- [Java CallGraph](https://github.com/gousiosg/java-callgraph)
