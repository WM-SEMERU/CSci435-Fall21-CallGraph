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
            (preproc_include
                path: (string_literal) @import)
            """)
    call_q = language_library.query("""
            (call_expression) @call
            (declaration
                declarator: (init_declarator) @call
                declarator: (function_declarator) @call)
            """)
    
    def get_call_print(self,call):
        callf = call.child_by_field_name('function')
        name = ''
        if callf.type == 'identifier':
            name = self.node_to_string(callf)
        elif callf.type == 'qualified_identifier':
            name = self.node_to_string(callf.child_by_field_name('name'))
        else:
            name = self.node_to_string(callf.child_by_field_name('field'))
        nargs = (len(call.child_by_field_name('arguments').children) - 1)//2
        return (name.split('<')[0],None)
        

    def get_method_print(self, method):
        name = self.node_to_string(method.child_by_field_name('declarator')).split('(')[0]
        nparams = (len(method.child_by_field_name('declarator').child_by_field_name('parameters').children) - 1)//2
        return (name, nparams)

    def get_import_file(self, imp):
        file_to_search = self.node_to_string(imp).strip('\"')
        return file_to_search