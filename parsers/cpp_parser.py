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
            (declaration) @call
            """)
    
    def get_call_print(self,call):
        if call.type == 'declaration':
            name = self.node_to_string(call.child_by_field_name('type'))
            declar = call.child_by_field_name('declarator')
            if declar.type == 'identifier':
                nargs = 0
            elif declar.type == 'init_declarator':
                nargs = (len(declar.child_by_field_name('value').child_by_field_name('arguments').children) - 1) // 2
        elif call.type == 'call_expression':
            func = call.child_by_field_name('function')
            name = self.node_to_string(func) if func.type == 'identifier' else self.node_to_string(func.child_by_field_name('field'))
            nargs = (len(call.child_by_field_name('arguments').children) - 1) // 2
        return (name, nargs)

    def get_method_print(self, method):
        signature = method.child_by_field_name('declarator')
        name = signature.child_by_field_name('declarator')
        name = self.node_to_string(name) if name.type == 'identifier' else self.node_to_string(name.child_by_field_name('name'))
        params = signature.child_by_field_name('parameters').children
        nparams = 0
        for param in params:
            if param.type == 'parameter_declaration' and self.node_to_string(param) != 'void':
                nparams += 1
        parent = method.parent
        parent_class = None
        while parent.type != 'translation_unit':
            if parent.type == 'class_specifier':
                parent_class = self.node_to_string(parent.child_by_field_name('name'))
            parent = parent.parent
        return (name, nparams)

    def get_import_file(self, imp):
        print(imp.child_by_field_name("path").children)
        return self.node_to_string(imp.child_by_field_name("path"))[1:-1]