from tree_sitter import Language
class Language:
    def __init__(self, language):
        if language == "python":
            self.language = "python"
            self.extension = ".py"
            self.language_library = Language("build/my-languages.so", "python)")
            self.terminology = ["function_definition", "class_definition"]