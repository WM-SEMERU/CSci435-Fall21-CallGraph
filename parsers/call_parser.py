from abc import ABC, abstractmethod
import os
class CallParser():
    __metaclass__ = ABC
    src_code = ''
    lines = []
    filepath = ''
    @property
    @abstractmethod
    def language(self):
        pass

    @property
    @abstractmethod
    def extension(self):
        pass

    @property
    @abstractmethod
    def language_library(self):
        pass

    @property
    @abstractmethod
    def PARSER(self):
        pass

    @property
    @abstractmethod
    def method_import_q(self):
        pass

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

    def node_to_string(self, node) -> str:
        start_point = node.start_point
        end_point = node.end_point
        if start_point[0] == end_point[0]:
            return self.lines[start_point[0]][start_point[1]:end_point[1]]
        ret = self.lines[start_point[0]][start_point[1]:] + "\n"
        ret += "\n".join([line for line in self.lines[start_point[0] + 1:end_point[0]]])
        ret += "\n" + self.lines[end_point[0]][:end_point[1]]
        return ret

    @abstractmethod
    def get_call_print(self, call) -> tuple:
        pass
    
    @abstractmethod
    def get_method_print(self, method) -> tuple:
        pass

    def get_import_file(self, imp):
        file_to_search = self.node_to_string(imp)
        return file_to_search.replace(".", os.sep) + self.extension