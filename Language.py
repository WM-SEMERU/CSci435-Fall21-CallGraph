from tree_sitter import Language, Parser

from parser_with_input import parse_python
class Language:
    def __init__(self, language):
        if language == "python":
            self.language = "python"
            self.extension = ".py"
            self.language_library = Language("build/my-languages.so", "python")
            self.terminology = ["function_definition", "class_definition"]
            self.query = self.language_library.query("""
                (function_definition) @method
                (import_statement) @import
                (import_from_statement) @import_from
                (call) @call
                (lambda) @lambda 
                """)
        elif language == "java":
            self.language = "java"
            self.extension = ".java"
            self.language_library = Language("build/my-languages.so", "java")
            self.terminology = ["method_declaration", "class_declaration"]
            self.query = self.language_library.query("""
                (method_declaration) @method
                (import_declaration) @import
                """)    

    def parse(self, src_code, method_nodes, import_nodes):
        parser = Parser()
        parser.set_language(self.language_library)
        tree = self.parser.parse(bytes(src_code, "utf8"))
        captures = self.query.captures(tree.root_node)
        method_nodes = [node[0] for node in captures if node[1] == 'method']
        import_nodes = [node[0] for node in captures if node[1] == 'import' or node[1] == 'import_from']