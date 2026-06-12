import ast

class RuleEngine(ast.NodeVisitor):
    def __init__(self):
        self.issues = []
        self.assigned = set()
        self.assigned_lines = {}
        self.used = set()
        self.imported_names = {}

    def visit_Import(self, node):
        for name in node.names:
            alias = name.asname or name.name
            self.imported_names[alias] = node.lineno
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for name in node.names:
            alias = name.asname or name.name
            self.imported_names[alias] = node.lineno
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # Long function check
        if len(node.body) > 10:
            self.issues.append({
                "line": node.lineno,
                "column": node.col_offset,
                "severity": "warning",
                "category": "complexity",
                "message": f"Function '{node.name}' is too long ({len(node.body)} lines)"
            })

        # Mutable default argument check
        for arg in node.args.defaults:
            if isinstance(arg, (ast.List, ast.Dict, ast.Set)):
                self.issues.append({
                    "line": arg.lineno if hasattr(arg, 'lineno') else node.lineno,
                    "column": arg.col_offset if hasattr(arg, 'col_offset') else node.col_offset,
                    "severity": "warning",
                    "category": "bug",
                    "message": f"Function '{node.name}' has mutable default argument"
                })

        # Missing docstring check
        if not ast.get_docstring(node):
            if not (node.name.startswith("__") and node.name.endswith("__")):
                self.issues.append({
                    "line": node.lineno,
                    "column": node.col_offset,
                    "severity": "info",
                    "category": "documentation",
                    "message": f"Function '{node.name}' is missing a docstring"
                })

        self.generic_visit(node)

    def visit_ClassDef(self, node):
        # Missing docstring check
        if not ast.get_docstring(node):
            self.issues.append({
                "line": node.lineno,
                "column": node.col_offset,
                "severity": "info",
                "category": "documentation",
                "message": f"Class '{node.name}' is missing a docstring"
            })
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.assigned.add(target.id)
                self.assigned_lines[target.id] = node.lineno
            elif isinstance(target, ast.Tuple) or isinstance(target, ast.List):
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        self.assigned.add(elt.id)
                        self.assigned_lines[elt.id] = node.lineno
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        if isinstance(node.target, ast.Name):
            self.assigned.add(node.target.id)
            self.assigned_lines[node.target.id] = node.lineno
        self.generic_visit(node)

    def visit_Name(self, node):
        # Track usage
        if isinstance(node.ctx, ast.Load):
            self.used.add(node.id)

        # Rule 2: Bad variable name
        if len(node.id) == 1 and node.id not in ("_", "i", "j", "k", "x", "y", "z"):
            self.issues.append({
                "line": node.lineno,
                "column": node.col_offset,
                "severity": "info",
                "category": "style",
                "message": f"Variable '{node.id}' name might be too short / non-descriptive"
            })

    def visit_While(self, node):
        # Possible infinite loop
        if isinstance(node.test, ast.Constant) and node.test.value is True:
            self.issues.append({
                "line": node.lineno,
                "column": node.col_offset,
                "severity": "warning",
                "category": "bug",
                "message": "Possible infinite loop detected (while True)"
            })
        self.generic_visit(node)

    def visit_BinOp(self, node):
        # Division by zero risk
        if isinstance(node.op, ast.Div):
            if isinstance(node.right, ast.Constant) and node.right.value == 0:
                self.issues.append({
                    "line": node.lineno,
                    "column": node.col_offset,
                    "severity": "critical",
                    "category": "bug",
                    "message": "Division by zero detected"
                })
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        # Bare except check
        if node.type is None:
            self.issues.append({
                "line": node.lineno,
                "column": node.col_offset,
                "severity": "warning",
                "category": "bug",
                "message": "Bare 'except:' handler detected (should catch specific exceptions)"
            })
        self.generic_visit(node)

    def visit_Call(self, node):
        # Dangerous functions eval/exec
        if isinstance(node.func, ast.Name):
            if node.func.id in ("eval", "exec"):
                self.issues.append({
                    "line": node.lineno,
                    "column": node.col_offset,
                    "severity": "critical",
                    "category": "security",
                    "message": f"Use of dangerous function '{node.func.id}' detected"
                })
        self.generic_visit(node)

    def finalize(self):
        # Unused variables (excluding standard short loop index variables)
        unused = self.assigned - self.used
        for var in unused:
            if var not in ("_", "i", "j", "k"):
                self.issues.append({
                    "line": self.assigned_lines.get(var, 1),
                    "column": 0,
                    "severity": "warning",
                    "category": "style",
                    "message": f"Variable '{var}' assigned but never used"
                })

        # Unused imports
        unused_imports = set(self.imported_names.keys()) - self.used
        for imp in unused_imports:
            self.issues.append({
                "line": self.imported_names[imp],
                "column": 0,
                "severity": "warning",
                "category": "style",
                "message": f"Imported module/name '{imp}' is never used"
            })
