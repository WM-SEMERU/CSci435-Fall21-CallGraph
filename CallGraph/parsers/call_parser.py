import os
from abc import ABC, abstractmethod
import os
class CallParser():
    __metaclass__ = ABC
    src_code = ''   #A string containing all the source code of the filepath
    lines = []      #All the lines in the current file
    filepath = ''  #the path to the current file

    """A string holding the name of the language, ex: 'python' """
    @property
    @abstractmethod
    def language(self):
        pass

    """A string holding the file extension for the language, ex: '.java' """
    @property
    @abstractmethod
    def extension(self):
        pass

    """A tree-sitter Language object, build from build/my-languages.so """
    @property
    @abstractmethod
    def language_library(self):
        pass
    
    """A tree-sitter Parser object"""
    @property
    @abstractmethod
    def PARSER(self):
        pass

    """The query that finds the method definitions (including constructors) and import statements"""
    @property
    @abstractmethod
    def method_import_q(self):
        pass

    """The query that finds all the function calls in the file"""
    @property
    @abstractmethod
    def call_q(self):
        pass

    """Sets the current file and updates the src_code and lines"""
    def set_current_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                self.src_code = file.read()
                self.lines = self.src_code.split('\n')
                self.filepath = path
        except FileNotFoundError as err:
            print(err)

    """Takes in a tree-sitter node object and returns the code that it refers to"""
    def node_to_string(self, node) -> str:
        start_point = node.start_point
        end_point = node.end_point
        if start_point[0] == end_point[0]:
            return self.lines[start_point[0]][start_point[1]:end_point[1]]
        ret = self.lines[start_point[0]][start_point[1]:] + "\n"
        ret += "\n".join([line for line in self.lines[start_point[0] + 1:end_point[0]]])
        ret += "\n" + self.lines[end_point[0]][:end_point[1]]
        return ret

    """Takes in a call node and returns a tuple of the name of the method that was called and the number of arguments passed
    for example, if passed the call node 'add(3, 4)' the function will return '(add, 2)'. See the Python, Java, and Cpp parsers
    for example implementations and use https://tree-sitter.github.io/tree-sitter/playground to view the structre of 
    a call node in the desired language"""
    @abstractmethod
    def get_call_print(self, name_node, arg_node) -> tuple:
        pass
    
    """Takes in a method node and returns a tuple of the name of the method and the number of parameters passed for example, 
    if passed the method node refering to 'def add(a,b)' the function will return '(add, 2)' see Java, Python, and Cpp parsers 
    for an example implementation, and use https://tree-sitter.github.io/tree-sitter/playground to view the structre of 
    a method call in the desired language"""
    @abstractmethod
    def get_method_print(self, name_node, param_node) -> tuple:
        pass

    """Takes in an import node and returns the path of the file that is imported
    don't wory about filtering out system libraries, as the program will check if the file exitsts before trying to add
    it to the project. You may need to override this method depending on how the language handles imports"""
    def get_import_file(self, imp):
        file_to_search = self.node_to_string(imp)
        return file_to_search.replace(".", os.sep) + self.extension
