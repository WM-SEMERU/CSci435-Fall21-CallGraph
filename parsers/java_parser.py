from .call_parser import CallParser
from tree_sitter import Language, Parser
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
            """)

    def get_call_print(self, name_node, arg_node):
        # gets the name of the method call
        name = self.node_to_string(name_node)
        # gets the number of arguments passed to the method
        nargs = (len(arg_node.children) - 1) // 2
        return (name, nargs)
    
    def get_method_print(self, name_node, param_node):
        name = self.node_to_string(name_node)
        nparams = (len(param_node.children) - 1) // 2
        return (name, nparams)

    def get_import_file(self, imp_node):
        return self.node_to_string(imp_node)
