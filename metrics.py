from radon.complexity import cc_visit

def get_complexity(code):
    results = cc_visit(code)
    output = []

    for r in results:
        output.append({
            "name": r.name,
            "complexity": r.complexity
        })

    return output