def find_duplicates(code, min_lines=2):
    lines = code.split("\n")
    cleaned = []
    original_indices = []

    # Filter out empty, comments, and trivial structural lines
    for i, raw_line in enumerate(lines):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        # Ignore trivial keywords/brackets that commonly repeat
        if line in (
            "pass", "return", "return True", "return False", "return None",
            "break", "continue", "self.generic_visit(node)", "else:", "try:", "finally:"
        ):
            continue
        if line in ("}", ")", "]", "},", "),", "],"):
            continue
        if len(line) < 4:
            continue

        cleaned.append(line)
        original_indices.append(i + 1)

    duplicates = []
    n = len(cleaned)
    matched = set()

    for i in range(n):
        if i in matched:
            continue
        # Search for duplicate blocks down the list
        for j in range(i + min_lines, n):
            k = 0
            while i + k < j and j + k < n and cleaned[i + k] == cleaned[j + k]:
                k += 1

            if k >= min_lines:
                start_line_1 = original_indices[i]
                end_line_1 = original_indices[i + k - 1]
                start_line_2 = original_indices[j]
                end_line_2 = original_indices[j + k - 1]
                block_content = "\n".join(cleaned[i:i + k])

                duplicates.append({
                    "start1": start_line_1,
                    "end1": end_line_1,
                    "start2": start_line_2,
                    "end2": end_line_2,
                    "line_count": k,
                    "content": block_content
                })

                # Mark these lines as processed to prevent duplicate matching
                for m in range(k):
                    matched.add(i + m)
                    matched.add(j + m)
                break

    return duplicates
