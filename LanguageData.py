from tree_sitter import Language, Parser
class LanguageData:
    def __init__(self, language):
        self.PARSER = Parser()
        if language == 'python' or language == 'py':
            self.language = 'python'
            self.extension = ".py"
            self.language_library = Language('build/my-languages.so', 'python')
            self.PARSER.set_language(self.language_library)
            self.method_import_q = self.language_library.query("""
            (function_definition) @method
            (import_statement) @import
            (import_from_statement) @import
            """)
            self.call_q = self.language_library.query("""
            (call) @call
            (lambda) @call
            """)
        elif language == 'java' or language == 'jv':
            self.language = 'java'
            self.extension = ".java"
            self.language_library = Language('build/my-languages.so', 'java') 
            self.PARSER.set_language(self.language_library)
            self.method_import_q = self.language_library.query("""
            (method_declaration) @method
            (constructor_declaration) @method
            (import_declaration) @import 
            """)
            self.call_q = self.language_library.query("""
            (method_invocation) @call
            (object_creation_expression) @call 
            """)
        else:
            raise ValueError("Unknown language: %s" % language)