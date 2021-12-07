import setuptools

setuptools.setup(
    name='call_graph_generator',
    version='0.0.1',
    author='',
    author_email='',
    description='a package to generate call graphs',
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    license='MIT',
    url='git@github.com:WM-SEMERU/CSci435-Fall21-CallGraph.git',
    install_requires=[
        'tree-sitter >= 0.19.0',
        'pandas >= 1.3.3',
        'gitpython >= 3.1.24'
    ],
	python_requires=">=3.9",
	packages=['src', 'parsers'],
    package_dir={'src': 'src', 'parsers': 'src/parsers'},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)