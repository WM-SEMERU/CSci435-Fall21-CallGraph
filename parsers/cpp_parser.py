from .call_parser import CallParser
from tree_sitter import Language, Parser
class CppParser(CallParser):
    language = "cpp"
    extension = ".cpp"
    language_library = Language('build/my-languages.so', 'cpp')
    PARSER = Parser()
    PARSER.set_language(language_library)
    method_import_q = language_library.query("""
            (function_definition
                declarator: (function_declarator
                    declarator: (identifier) @method_name
                    parameters: (parameter_list) @method_params)) @method
            (preproc_include
                path: (string_literal) @import)
            """)
    call_q = language_library.query("""
            (call_expression
                function: [
                    (qualified_identifier
                        name: (identifier) @function_name)
                    (identifier) @function_name
                    (field_expression
                        field: (field_identifier) @function_name)]
                arguments: (argument_list) @arguments
            ) @function
            (declaration
                type: (type_identifier) @function_name
                declarator: [
                    (init_declarator
                        declarator: (identifier) @function_name
                        value: (argument_list) @arguments)
                    (function_declarator 
                        declarator: (identifier) @function_name
                        parameters: (parameter_list) @arguments)
            ]) @function
            (assignment_expression
                left: (identifier) @function_name
                right: (lambda_expression
                    declarator: (abstract_function_declarator
                        parameters: (parameter_list) @arguments))
            ) @function
            """)
    
    def get_call_print(self,name_node,arg_node) -> tuple:
        name = self.node_to_string(name_node)
        nargs = (len(arg_node.children) - 1)//2
        return (name,nargs)
        

    def get_method_print(self, name_node,param_node) -> tuple:
        name = self.node_to_string(name_node)
        nparams = (len(param_node.children) - 1)//2
        for child in param_node.children:
            if self.node_to_string(child) == 'void':
                return (name, 0)
        return (name, nparams)

    def get_import_file(self, imp) -> str:
        file_to_search = self.node_to_string(imp)
        return file_to_search[1:-1]
