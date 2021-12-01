from .call_parser import CallParser
from tree_sitter import Language, Parser
class CppParser(CallParser):
    language = "cpp"
    extension = ".cpp"
    language_library = Language('build/my-languages.so', 'cpp')
    PARSER = Parser()
    PARSER.set_language(language_library)
    method_import_q = language_library.query("""
            (function_definition) @method
            (preproc_include) @import
            """)
    call_q = language_library.query("""
            (call_expression) @call
            (declaration
                declarator: (init_declarator) @call
                declarator: (function_declarator) @call)
            """)
    
    def get_call_print(self,call):
        pass

    def get_method_print(self, method):
        pass

    def get_import_file(self, imp):
        pass