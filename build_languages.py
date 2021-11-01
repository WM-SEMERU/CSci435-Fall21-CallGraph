from tree_sitter import Language

def main():
    Language.build_library(
    'build/my-languages.so',
    [
        'vendor/tree-sitter-python',
        'vendor/tree-sitter-java'
    ]
)

if __name__ == '__main__':
    main()