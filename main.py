import sys
from parser import CodeParser
from rules import RuleEngine
from metrics import get_complexity
from duplicates import find_duplicates
from suggestions import generate_suggestions
from ai_model import AICodeAnalyzer


class CodeAnalyzer:
    def __init__(self, code):
        self.code = code

    def calculate_score(self, issues, complexity, duplicates):
        score = 10.0

        # Penalize issues by severity
        for issue in issues:
            if isinstance(issue, dict):
                sev = issue.get("severity", "warning")
                if sev == "critical":
                    score -= 2.0
                elif sev == "warning":
                    score -= 0.8
                else:  # info
                    score -= 0.2
            else:
                score -= 0.5

        # Penalize complexity
        for func in complexity:
            if func.get("complexity", 1) > 5:
                score -= 1.0

        # Penalize duplicate blocks
        score -= len(duplicates) * 0.5

        # Ensure score is bound between 0.0 and 10.0
        return max(round(score, 1), 0.0)

    def analyze(self):
        parser = CodeParser(self.code)
        tree = parser.parse()

        if isinstance(tree, dict) and "error" in tree:  # syntax error
            return {
                "score": 0.0,
                "issues": [{
                    "line": 1,
                    "column": 0,
                    "severity": "critical",
                    "category": "syntax",
                    "message": f"Syntax Error: {tree['error']}"
                }],
                "complexity": [],
                "duplicates": [],
                "suggestions": ["Fix the syntax error in the code before proceeding."],
                "ai_analysis": {
                    "ai_bug_risk": True,
                    "confidence": 1.0,
                    "message": f"Syntax Error makes code unrunnable: {tree['error']}",
                    "bug_details": [],
                    "suggested_fix": self.code
                }
            }

        # Rule engine
        engine = RuleEngine()
        engine.visit(tree)
        engine.finalize()

        # Metrics
        complexity = get_complexity(self.code)

        # Duplicate detection
        duplicates = find_duplicates(self.code)

        # Suggestions
        suggestions = generate_suggestions(engine.issues)

        # AI analysis
        ai = AICodeAnalyzer()
        ai_result = ai.analyze(self.code)

        # Score
        score = self.calculate_score(engine.issues, complexity, duplicates)

        return {
            "score": score,
            "issues": engine.issues,
            "complexity": complexity,
            "duplicates": duplicates,
            "suggestions": suggestions,
            "ai_analysis": ai_result
        }


def run_cli():
    if len(sys.argv) < 2:
        print("Usage: python main.py <file.py>")
        return

    file_path = sys.argv[1]

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
    except FileNotFoundError:
        print("File not found!")
        return

    analyzer = CodeAnalyzer(code)
    result = analyzer.analyze()

    # If the first issue is syntax error
    if result["issues"] and result["issues"][0].get("category") == "syntax":
        print("\nSyntax Error:")
        print(result["issues"][0]["message"])
        return

    print("\n=== Code Analysis Report ===")
    print(f"\nScore: {result['score']}/10")

    print("\nIssues:")
    if result["issues"]:
        for issue in result["issues"]:
            print(f"- Line {issue['line']}: [{issue['severity'].upper()}] {issue['message']}")
    else:
        print("No issues found 🎉")

    print("\nComplexity:")
    if result["complexity"]:
        for func in result["complexity"]:
            print(f"- {func['name']}: {func['complexity']}")
    else:
        print("No complex functions found")

    print("\nDuplicate Blocks:")
    if result["duplicates"]:
        for d in result["duplicates"]:
            print(f"- Lines {d['start1']}-{d['end1']} duplicate of Lines {d['start2']}-{d['end2']}:\n  {d['content']}")
    else:
        print("No duplicates found")

    print("\nSuggestions:")
    if result["suggestions"]:
        for s in result["suggestions"]:
            print(f"- {s}")
    else:
        print("No suggestions")

    print("\nAI Analysis:")
    ai = result["ai_analysis"]
    print(f"- Bug Risk: {ai['ai_bug_risk']}")
    print(f"- Confidence: {ai['confidence']}")
    print(f"- Summary: {ai['message']}")


if __name__ == "__main__":
    run_cli()
