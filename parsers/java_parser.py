from parsers.call_parser import CallParser
from tree_sitter import Language, Parser
class JavaParser(CallParser):
    language = 'java'
    extension = '.java'
    language_library = Language('build/my-languages.so', 'java')
    PARSER = Parser()
    PARSER.set_language(language_library)
    method_import_q = language_library.query("""
            (method_declaration) @method
            (constructor_declaration) @method
            (import_declaration) @import 
            """)
    call_q = language_library.query("""
            (method_invocation) @call
            (object_creation_expression) @call 
            """)

    def get_call_print(self, node):
        # gets the name of the method call
        if node.type == 'method_invocation':
            name = self.node_to_string(node.child_by_field_name('name'))
        elif node.type == 'object_creation_expression':
            name = self.node_to_string(node.child_by_field_name('type'))
        # gets the number of arguments passed to the method
        nargs = (len(node.child_by_field_name('arguments').children) - 1) // 2
        return (name, nargs)
    
    def get_method_print(self, method):
        name = self.node_to_string(method.child_by_field_name('name'))
        nparams = (len(method.child_by_field_name('parameters').children) - 1) // 2
        parent = method.parent
        parent_class = None
        while parent.type != 'program':
            if parent.type == 'class_declaration':
                parent_class = self.node_to_string(parent.child_by_field_name('name'))
                break
            parent = parent.parent
        return (name, nparams)

    def get_import_file(self, imp):
        for child in imp.children[1:]:
                if child.type == 'identifier' or child.type == 'scoped_identifier':
                    return self.node_to_string(child)