def generate_suggestions(issues):
    suggestions = []

    for issue in issues:
        # Resolve issue content if it's a structured dictionary or string
        msg = issue["message"] if isinstance(issue, dict) else issue
        
        if "too long" in msg:
            suggestions.append("Break down complex, long functions into smaller, single-purpose helper functions.")

        elif "name might be too short" in msg or "name too short" in msg:
            suggestions.append("Use descriptive variable names (e.g. user_id instead of u) to clarify code intent.")

        elif "assigned but never used" in msg:
            suggestions.append("Remove unused variables to keep local scopes clean and readable.")

        elif "never used" in msg and "Imported" in msg:
            suggestions.append("Remove unused imports to optimize execution and keep dependencies clean.")

        elif "mutable default argument" in msg:
            suggestions.append("Use None as default parameter, then initialize mutable types (e.g., list, dict) inside the function.")

        elif "infinite loop" in msg:
            suggestions.append("Verify the loop condition can evaluate to False, or that it has an explicit 'break' statement.")

        elif "division by zero" in msg:
            suggestions.append("Ensure divisor operands are validated to be non-zero before performing division.")

        elif "Bare 'except:' handler" in msg:
            suggestions.append("Specify explicit exception classes (e.g. except ValueError:) to avoid trapping system exit events.")

        elif "dangerous function" in msg:
            suggestions.append("Avoid eval() or exec() as they pose severe code injection risks. Implement custom parsing or standard methods.")

        elif "missing a docstring" in msg:
            suggestions.append("Add descriptive docstrings to functions and classes to document public APIs and parameters.")

    return list(set(suggestions))