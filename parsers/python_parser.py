from parsers.call_parser import CallParser
from tree_sitter import Language, Parser
import os
class PythonParser(CallParser):
    language = 'python'
    extension = '.py'
    language_library = Language('build/my-languages.so', 'python')
    PARSER = Parser()
    PARSER.set_language(language_library)
    method_import_q = language_library.query("""
            (function_definition) @method
            (import_statement
                name: (dotted_name) @import)
            (import_from_statement
                module_name: (dotted_name) @import)
            """)
    call_q = language_library.query("""
            (call) @call
            (lambda) @call
            """)

    def get_call_print(self, node):
        # gets the name of the method call
        func = node.child_by_field_name('function') 
        try:
            name = self.node_to_string(func) if func.type == 'identifier' else self.node_to_string(func.child_by_field_name('attribute'))
        except Exception:
            name = None
        # gets the number of arguments passed to the method
        nargs = (len(node.child_by_field_name('arguments').children) - 1) // 2
        print(name)
        return (name, nargs)
    
    def get_method_print(self, method):
        name = self.node_to_string(method.child_by_field_name('name'))
        param_node = method.child_by_field_name('parameters')
        if param_node is None:
            nparams = 0
        else:
            params = param_node.children
            nparams = (len(params) - 1) // 2
            for param in params:
                if self.node_to_string(param) == 'self':
                    nparams -= 1
        parent = method.parent
        parent_class = None
        while parent.type != 'module':
            if parent.type == 'class_definition':
                parent_class = self.node_to_string(parent.child_by_field_name('name'))
                if name == '__init__':
                    name = parent_class
                break
            parent = parent.parent
        return (name, nparams)

    # def get_import_file(self, imp):
    #     file_to_search = self.node_to_string(imp)
    #     return file_to_search.replace(".", os.sep) + self.extension