# AI Code Analyzer for Bug Detection and Code Quality Analysis

A state-of-the-art web-based developer tool designed to perform rapid static code analysis, function complexity mapping, duplication detection, and AI-powered refactoring.

🚀 **Live Deployment (Frontend)**: [https://ai-code-analyzer-5xcq.vercel.app/](https://ai-code-analyzer-5xcq.vercel.app/)

Built using a hybrid framework, the app leverages **Python AST Parsing**, **Radon**, **Pylint** rules, and **Google Gemini API** (with a local fallback engine) to score your code quality and pinpoint bugs, styling errors, or security risks.

---

## Key Features

*   **Premium Web Workspace (UI/UX)**: Styled using a modern glassmorphic dark theme, incorporating custom radial glow gradients, transitions, and animated quality gauges.
*   **VS Code-like Code Editor**: Employs **Monaco Editor** via CDN. Paste, type, edit, or upload files directly.
*   **Integrated Rule Engine**: Check for bad practices:
    *   *Bug detection*: Infinite loops, division by zero risks, mutable default arguments, bare except blocks.
    *   *Security analysis*: Insecure use of dangerous functions (`eval`, `exec`).
    *   *Style & Quality*: Unused imports, unused variables, short/non-descriptive variables, missing function/class docstrings.
*   **Monaco Line Linkage**: Clicking on any reported issue in the panel automatically scrolls the editor and highlights the exact line of code.
*   **Complexity Mapping**: Renders cyclomatic function complexity charts using **Chart.js** alongside color-coded severity metrics (Green = Safe, Orange = Warning, Red = Refactor).
*   **Code Duplication Block Finder**: Identifies multi-line duplicate blocks (consecutive lines) in code while ignoring blank lines and common trivial phrases.
*   **Gemini Refactoring Diff**: Connects directly to Gemini models to get structured AI bug reports and a side-by-side **Monaco Diff Editor** showing original vs. refactored suggestions.

---

## Installation & Setup

1.  **Clone or Open the Workspace**:
    ```bash
    cd AI-CODE-ANALYZER
    ```

2.  **Install Required Python Libraries**:
    Make sure you have Python 3.8+ installed. Install dependencies using:
    ```bash
    pip install -r requirements.txt
    ```

3.  **(Optional) Set up Gemini API Key**:
    To unlock deep AI reviews, set your API key as an environment variable:
    *   **Windows (Command Prompt)**:
        ```cmd
        set GEMINI_API_KEY=your_gemini_api_key_here
        ```
    *   **Windows (PowerShell)**:
        ```powershell
        $env:GEMINI_API_KEY="your_gemini_api_key_here"
        ```
    *   **Linux/macOS**:
        ```bash
        export GEMINI_API_KEY="your_gemini_api_key_here"
        ```
    *   *If no key is configured, the system automatically falls back to local AST security heuristics and style checks.*

---

## How to Run

1.  **Start the API Server**:
    Launch the server using Uvicorn:
    ```bash
    uvicorn api:app --reload --port 8000
    ```

2.  **Access the Dashboard**:
    Open your favorite browser and navigate to:
    ```
    http://127.0.0.1:8000/
    ```

3.  **Run CLI Mode (Alternative)**:
    You can also analyze files directly in your terminal:
    ```bash
    python main.py sample_code.py
    ```

---

## Deployment

This project is configured for split-architecture cloud deployment:
*   **Frontend**: Hosted on **Vercel** at [https://ai-code-analyzer-5xcq.vercel.app/](https://ai-code-analyzer-5xcq.vercel.app/) (utilizing the static deployment instructions in `vercel.json`).
*   **Backend API**: Hosted on **Render** (utilizing the `render.yaml` service blueprint).

*Note: Once deployed, open the Vercel app, click on the API connection status badge in the header, and paste your Render backend web service URL to link the two.*

---

## Project Architecture

```
AI-CODE-ANALYZER/
│
├── api.py            # FastAPI Web Server (handles routes, serves index.html)
├── main.py           # Core Analyzer Coordinator & CLI tool
├── rules.py          # AST-based static validation checks (RuleEngine)
├── duplicates.py     # Duplicate code block detection algorithm
├── metrics.py        # Cyclomatic complexity check (via Radon)
├── suggestions.py    # Maps issue codes to action recommendations
├── ai_model.py       # Dual-mode AI analysis (Gemini API + Local fallback)
├── parser.py         # Source code to AST translator
│
├── index.html        # Interactive Single Page Application (Monaco, Chart.js)
├── requirements.txt  # Project libraries list
└── readme.md         # Project guide
```

<!-- Extra readme instructions and guidelines -->
