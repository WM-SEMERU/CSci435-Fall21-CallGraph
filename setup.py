import setuptools

setuptools.setup(
    name='call_graph_generator',
    version='0.0.1',
    author='WMSEMERU-CS435-CallGraphGeneratorTeam',
    author_email='TODO',
    description='a package to generate call graphs',
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    url='git@github.com:WM-SEMERU/CSci435-Fall21-CallGraph.git',
    package_dir={"": "src"},
    packages=['src', 'src.parsers'],
    include_package_data=True,
    
)