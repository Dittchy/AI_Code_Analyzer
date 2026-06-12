import ast

class CodeParser:
    def __init__(self, code):
        self.code = code
        self.tree = None

    def parse(self):
        try:
            self.tree = ast.parse(self.code)
            return self.tree
        except SyntaxError as e:
            return {
                "error": str(e),
                "lineno": e.lineno or 1,
                "offset": e.offset or 0
            }