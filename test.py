from call_parser import CallParser
from python_parser import PythonParser

thing = PythonParser()

code = """
def foo(x):
    if bar():
        baz()"""


thing.set_current_file("test/test.py")
tree = thing.PARSER.parse(bytes(thing.src_code, "utf8"))
query = thing.method_import_q
captures = [node[0] for node in query.captures(tree.root_node) if node[1] == 'method']
query = thing.call_q
for node in captures:
    calls = query.captures(node)
    for call in calls:
        print(thing.get_call_print(call[0]))
