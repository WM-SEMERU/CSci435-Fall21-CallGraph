from tree_sitter import Language, Parser

from parser_with_input import parse_python
class Language:
    def __init__(self, language):
        if language == "python":
            self.language = "python"
            self.extension = ".py"
            self.language_library = Language("build/my-languages.so", "python")
            self.terminology = ["function_definition", "class_definition"]
        elif language == "java":
            self.language = "java"
            self.extension = ".java"
            self.language_library = Language("build/my-languages.so", "java")
            self.terminology = ["method_declaration", "class_declaration"]

        self.parser = Parser()

    def parse(self, src_code):
        if self.language == "python":
            self.parse_python(src_code)
        elif self.language == "java":
            self.parse_java(src_code)

    def parse_python(self, src_code):
        self.parser.set_language(self.language_library)
        global tree
        tree = self.parser.parse(bytes(src_code, "utf8"))

        query = self.language_library.query("""
        (function_definition) @method
        (import_statement) @import
        (import_from_statement) @import_from
        """)
        captures = query.captures(tree.root_node)
        method_nodes = [node[0] for node in captures if node[1] == 'method']
        import_nodes = [node[0] for node in captures if node[1] == 'import' or node[1] == 'import_from']
        method_df['methods'].extend([node_to_string(node) for node in method_nodes])

        imports = []
        for imp in import_nodes:
            file_to_search, name_to_search, thing_to_search = None, None, None
            if imp.type == 'import_statement':
                node = imp.child_by_field_name('name')
                if node.type == 'aliased_import':
                    file_to_search = node_to_string(node.child_by_field_name('name'))
                    name_to_search = node_to_string(node.child_by_field_name('alias'))
                else:
                    file_to_search = node_to_string(node)
            elif imp.type == 'import_from_statement':
                file_to_search = node_to_string(imp.child_by_field_name('module_name'))
                node = imp.child_by_field_name('name')
                if node.type == 'aliased_import':
                    thing_to_search = node_to_string(node.child_by_field_name('name'))
                    name_to_search = node_to_string(node.child_by_field_name('alias'))
                else:
                    thing_to_search = node_to_string(node)
            imports.append(tuple([file_to_search.replace('.',os.sep), thing_to_search, name_to_search]))

        query = self.language_library.query("""
        (call) @call
        (lambda) @lambda
        """)
        for node in method_nodes:
            captures = query.captures(node)
            call_nodes = [call[0] for call in captures if call[1] == 'call']
            calls = [node_to_string(call) for call in call_nodes]

    def parse_java(self, src_code):
        self.parser.set_language(self.language_library)
        global tree
        tree = self.parser.parse(bytes(src_code, "utf8"))

        query = self.language_library.query("""
        (method_declaration) @method
        (import_declaration) @import
        """)
        captures = query.captures(tree.root_node)
        method_nodes = [node[0] for node in captures if node[1] == 'method']
        import_nodes = [node[0] for node in captures if node[1] == 'import']
        method_df['methods'].extend([node_to_string(node) for node in method_nodes])
        imports = []
        for imp in import_nodes:
            for child in imp.children[1:]:
                if child.type == 'identifier' or child.type == 'scoped_identifier':
                    ident_str = node_to_string(child)
                    break
            imports.append(ident_str.replace(".", os.sep))