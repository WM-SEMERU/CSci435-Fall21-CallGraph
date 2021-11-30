from call_parser import CallParser
from tree_sitter import Language, Parser
class PythonParser(CallParser):
    language = 'python'
    extension = '.py'
    language_library = Language('build/my-languages.so', 'python')
    PARSER = Parser()
    PARSER.set_language(language_library)
    method_import_q = language_library.query("""
            (function_definition) @method
            (import_statement) @import
            (import_from_statement) @import
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
        if node.child_by_field_name('arguments') is None:
            print(self.filepath)
            print(node.children)
            print(self.node_to_string(node))
        # gets the number of arguments passed to the method
        nargs = (len(node.child_by_field_name('arguments').children) - 1) // 2
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

    def get_import_file(self, imp):
        node = imp.child_by_field_name('name')
        if imp.type == 'import_statement':
            if node.type == 'aliased_import':
                file = self.node_to_string(node.child_by_field_name('name'))
            else:
                file = self.node_to_string(node)
        elif imp.type == 'import_from_statement':
            file = self.node_to_string(imp.child_by_field_name('module_name'))
        return file