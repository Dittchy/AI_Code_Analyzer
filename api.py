import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from main import CodeAnalyzer

app = FastAPI(title="AI Code Analyzer")

# Configure CORS so that frontends can communicate with this API easily
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeInput(BaseModel):
    code: str


@app.get("/", response_class=HTMLResponse)
async def read_index():
    """Serves the front-end application directly."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(current_dir, "index.html")
    
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="index.html not found")
        
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading index.html: {str(e)}")


@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    """Analyze code from an uploaded file."""
    try:
        content = await file.read()
        code = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Uploaded file must be a UTF-8 text file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

    analyzer = CodeAnalyzer(code)
    return analyzer.analyze()


@app.post("/analyze_text")
async def analyze_text(data: CodeInput):
    """Analyze code from a JSON text body."""
    if not data.code.strip():
        raise HTTPException(status_code=400, detail="Code content cannot be empty")
        
    analyzer = CodeAnalyzer(data.code)
    return analyzer.analyze()
