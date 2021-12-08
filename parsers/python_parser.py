from os import sep
from parsers.call_parser import CallParser
from tree_sitter import Language, Parser
class PythonParser(CallParser):
    language = 'python'
    extension = '.py'
    language_library = Language('build/my-languages.so', 'python')
    PARSER = Parser()
    PARSER.set_language(language_library)
    method_import_q = language_library.query("""
            (function_definition
                name: (identifier) @method_name
                parameters: (parameters) @method_params) @method
            (import_statement 
                name: (dotted_name) @import)
            (import_from_statement
                module_name: (dotted_name) @import)
            """)
    call_q = language_library.query("""
            (call
                function: [
                    (identifier) @function_name
                    (attribute
                    attribute: (identifier) @function_name)
                ]
                arguments: (argument_list) @arguments) @function
            (assignment
                left: (identifier) @function_name
                right: (lambda
                    parameters: (lambda_parameters) @arguments)
            ) @function
            """)

    def get_call_print(self, name_node, arg_node) -> tuple:
        # gets the name of the method call
        name = self.node_to_string(name_node) 
        # gets the number of arguments passed to the method
        nargs = (len(arg_node.children) - 1) // 2
        return (name, nargs)
    
    def get_method_print(self, name_node, param_node) -> tuple:
        name = self.node_to_string(name_node)
        nparams = (len(param_node.children) - 1) // 2
        for child in param_node.children:
            if self.node_to_string(child) == 'self':
                return (name, nparams - 1)
        return (name, nparams)

    def get_import_file(self, imp_node) -> str:
        return self.node_to_string(imp_node).replace(".", sep) + self.extension
