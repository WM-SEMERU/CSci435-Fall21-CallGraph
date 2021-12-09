from os import sep
from .call_parser import CallParser
from tree_sitter import Language, Parser
import os
class JavaParser(CallParser):
    language = 'java'
    extension = '.java'
    language_library = Language('build/my-languages.so', 'java')
    PARSER = Parser()
    PARSER.set_language(language_library)
    method_import_q = language_library.query("""
            (method_declaration
                name: (identifier) @method_name
                parameters: (formal_parameters) @method_params) @method
            (constructor_declaration
                name: (identifier) @method_name
                parameters: (formal_parameters) @method_params) @method
            (import_declaration
                [
                    (identifier) @import
                    (scoped_identifier) @import
                ]) 
            """)
            
    call_q = language_library.query("""
            (method_invocation
                name: (identifier) @function_name
                arguments: (argument_list) @arguments) @function
            (object_creation_expression
                type: (type_identifier) @function_name
                arguments: (argument_list) @arguments) @function
            (variable_declarator
                name: (identifier) @function_name
                value: (lambda_expression
                    parameters: (inferred_parameters) @arguments)
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
        if param_node is None:
            return (name, 0)
        nparams = (len(param_node.children) - 1) // 2
        for child in param_node.children:
            if self.node_to_string(child) == 'void':
                return (name, 0)
        return (name, nparams)

    def get_import_file(self, imp_node) -> str:
        return self.node_to_string(imp_node).replace('.', sep)
