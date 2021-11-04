from tree_sitter import Language
import os
import git
from pathlib import Path

def main():
    folder_path = os.path.join(os.path.dirname(__file__),"vendor")
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    repository_path = os.path.join(folder_path,"tree-sitter-python")
    if not os.path.exists(repository_path):
        git.Repo.clone_from("https://github.com/tree-sitter/tree-sitter-python", repository_path)
    repository_path = os.path.join(folder_path,"tree-sitter-java")
    if not os.path.exists(repository_path):
        git.Repo.clone_from("https://github.com/tree-sitter/tree-sitter-java", repository_path)
    
    Language.build_library(
    'build/my-languages.so',
    [
        'vendor/tree-sitter-python',
        'vendor/tree-sitter-java'
    ]
    )

if __name__ == '__main__':
    main()