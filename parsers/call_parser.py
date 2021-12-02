import os
from abc import ABC, abstractmethod
class CallParser():
    __metaclass__ = ABC

    # string value holding the name of the language (python, java, etc.)
    @property
    @abstractmethod
    def language(self):
        pass

    # string value holding the name of the extension on files of this language (.py, .java, etc.)
    property
    @abstractmethod
    def extension(self):
        pass

    # TreeSitter Language object for this language
    @property
    @abstractmethod
    def language_library(self):
        pass

    # TreeSitter Parser object for this language
    @property
    @abstractmethod
    def PARSER(self):
        pass

    # TreeSitter Query object to find the methods and import statements of this language
    @property
    @abstractmethod
    def method_import_q(self):
        pass

    # TreeSitter Query object to find the method calls of this language
    @property
    @abstractmethod
    def call_q(self):
        pass


    def set_current_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                self.src_code = file.read()
                self.lines = self.src_code.split('\n')
                self.filepath = path
        except FileNotFoundError as err:
            print(err)

    # Helper method to convert a TreeSitter Node to a string using the current file
    def node_to_string(self, node) -> str:
        start_point = node.start_point
        end_point = node.end_point
        if start_point[0] == end_point[0]:
            return self.lines[start_point[0]][start_point[1]:end_point[1]]
        ret = self.lines[start_point[0]][start_point[1]:] + "\n"
        ret += "\n".join([line for line in self.lines[start_point[0] + 1:end_point[0]]])
        ret += "\n" + self.lines[end_point[0]][:end_point[1]]
        return ret

    # method to get the print containing the name, and number of arguments of a method call
    @abstractmethod
    def get_call_print(self, name_node, arg_node) -> tuple:
        pass
    
    # method to get the print containing the name, and number of parameters of a method
    @abstractmethod
    def get_method_print(self, name_node, param_node) -> tuple:
        pass

    @abstractmethod
    def get_import_file(self, imp):
        file_to_search = self.node_to_string(imp)
        return file_to_search.replace(".", os.sep) + self.extension
