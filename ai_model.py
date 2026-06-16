import os
import json
import requests

class AICodeAnalyzer:
    def __init__(self):
        # Read API key from standard environment variables
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    def analyze(self, code):
        if self.api_key:
            try:
                return self._analyze_with_gemini(code)
            except Exception as e:
                # If the Gemini call fails, fall back to local rule-based diagnostics
                local_res = self._analyze_local(code)
                local_res["message"] = f"AI Analysis (Gemini API failed, fallback active): {local_res['message']}"
                return local_res
        else:
            return self._analyze_local(code)

    def _analyze_with_gemini(self, code):
        prompt = (
            "You are an expert AI code analyzer. Analyze the following Python code for bugs, security vulnerabilities, and quality issues.\n"
            "Respond ONLY with a JSON object containing the EXACT keys detailed below (no markdown wrappers inside the JSON values):\n"
            "{\n"
            "  \"ai_bug_risk\": true/false,\n"
            "  \"confidence\": 0.95,\n"
            "  \"message\": \"Concise overall summary of the code quality and findings\",\n"
            "  \"bug_details\": [\n"
            "    { \"line\": 12, \"category\": \"security | logic | style\", \"message\": \"Risk/bug description\" }\n"
            "  ],\n"
            "  \"suggested_fix\": \"The complete refactored/fixed Python code, formatted properly with identical indentations. Do not include markdown code block syntax here.\"\n"
            "}\n\n"
            "Code to analyze:\n"
            f"{code}"
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }

        # Timeout after 12 seconds to prevent locking the thread
        response = requests.post(url, json=payload, headers=headers, timeout=12)
        response.raise_for_status()

        result_json = response.json()
        text_response = result_json["candidates"][0]["content"]["parts"][0]["text"]

        # Parse JSON from text response
        analysis = json.loads(text_response.strip())
        return analysis

    def _analyze_local(self, code):
        bug_details = []
        confidence = 0.3
        ai_bug_risk = False
        lines = code.split("\n")

        # 1. SQL Injection Risk detection
        for idx, raw_line in enumerate(lines):
            line = raw_line.strip()
            if "select" in line.lower() and ("%s" in line or "f\"" in line or "f'" in line or "+" in line or ".format(" in line) and "from" in line.lower():
                bug_details.append({
                    "line": idx + 1,
                    "category": "security",
                    "message": "Potential SQL Injection risk. Avoid string formatting or f-strings in SQL statements. Use parameterized queries."
                })
                ai_bug_risk = True
                confidence = max(confidence, 0.8)

        # 2. Hardcoded secret detection
        for idx, raw_line in enumerate(lines):
            line = raw_line.strip()
            if ("api_key" in line.lower() or "secret" in line.lower() or "password" in line.lower() or "token" in line.lower()) and "=" in line:
                right_side = line.split("=", 1)[1].strip()
                if (right_side.startswith('"') and right_side.endswith('"')) or (right_side.startswith("'") and right_side.endswith("'")):
                    # Exclude empty quotes or trivial strings
                    cleaned_val = right_side[1:-1].strip()
                    if len(cleaned_val) > 4 and cleaned_val not in ("your_api_key", "password", "secret", "token"):
                        bug_details.append({
                            "line": idx + 1,
                            "category": "security",
                            "message": f"Potential hardcoded credential or secret key found: {right_side}. Use environment variables instead."
                        })
                        ai_bug_risk = True
                        confidence = max(confidence, 0.85)

        # 3. Deep Indentation check (Nested loop / condition risk)
        for idx, raw_line in enumerate(lines):
            line = raw_line.strip()
            leading_spaces = len(raw_line) - len(line)
            if leading_spaces >= 16:  # 4 levels of indentation (4 * 4 spaces)
                bug_details.append({
                    "line": idx + 1,
                    "category": "style",
                    "message": "Deep nesting indentation (16+ spaces). Consider refactoring inner blocks into helper functions."
                })
                confidence = max(confidence, 0.5)

        # 4. print statements in code
        for idx, raw_line in enumerate(lines):
            line = raw_line.strip()
            if line.startswith("print(") or " print(" in line:
                # Ignore in cli scripts or test prints
                if "run_cli" not in code and "__main__" not in code:
                    bug_details.append({
                        "line": idx + 1,
                        "category": "style",
                        "message": "Production code: Consider using Python's 'logging' module instead of 'print()' statements."
                    })
                    confidence = max(confidence, 0.4)

        if ai_bug_risk:
            message = "AI (Local Fallback) suggests the code may contain security or logic vulnerabilities."
        elif bug_details:
            message = "AI (Local Fallback) completed analysis and found structural improvements."
        else:
            message = "AI (Local Fallback) suggests the code looks structurally sound."

        # Basic suggestions for local fallback code fix (e.g. comment additions or mock improvements)
        suggested_fix = (
            "# AI Refactored Suggestions (Local Fallback Mode)\n"
            "# 1. Avoid inline SQL queries with raw string concatenation. Use DB-API parameterization.\n"
            "# 2. Load API keys, passwords, and tokens dynamically using os.environ.get('KEY').\n"
            "# 3. Extract nested loops or double loops into single-purpose modular functions.\n\n"
            + code
        )

        return {
            "ai_bug_risk": ai_bug_risk,
            "confidence": round(confidence, 2),
            "message": message,
            "bug_details": bug_details,
            "suggested_fix": suggested_fix
        }

# Extra AI fallback support functions
