from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Depends
from fastapi.responses import HTMLResponse,JSONResponse,FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from pydantic import BaseModel
import uvicorn
import os
import shutil
import magic
import Functions

# Initialize FastAPI app
app = FastAPI()

# Set up the templates directory for Jinja2
templates = Jinja2Templates(directory="/home/mostafabadboudi/Google_Doculate_Backup/site/")

# Serve static files (CSS, JS, etc.)
app.mount("/site", StaticFiles(directory="/home/mostafabadboudi/Google_Doculate_Backup/site"), name="HTML")
app.mount("/HomePageAssets", StaticFiles(directory="/home/mostafabadboudi/Google_Doculate_Backup/site/HomePageAssets"), name="HomePageAssets")

# Set up for file transfer 
# Allowed file types (MIME types)
ALLOWED_FILE_TYPES = {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"}

# Max file size (10 MB) 
MAX_FILE_SIZE = 10 * 1024 * 1024  

# Temporary storage directory
UPLOAD_DIR = "/home/mostafabadboudi/Google_Doculate_Backup/tmp" 
TRANSLATED_DIR = "/home/mostafabadboudi/Google_Doculate_Backup/tmp_translated" 
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TRANSLATED_DIR, exist_ok=True)

# Home page endpoint
@app.get("/", response_class=HTMLResponse)
def load_homepage(request: Request):
    return templates.TemplateResponse("homepage.html", {"request": request, "variable": "value"})

# File Upload end point
@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    source_lang: str = Form(...),
    target_lang: str = Form(...)):
   
    # Get file
    file_content = await file.read()

    # Check file size
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds the limit (10MB).")

    # Check file type
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(file_content)

    if file_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type. Only DOCX allowed.")

    # Save file to tmp storage
    file_path = os.path.join(UPLOAD_DIR, f"file_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(file_content)

    # translate uploaded file
    translated_path = Functions.full_operation(file_path,source_lang,target_lang)

    # Delete from tmp original file
    os.remove(file_path)

    # Return the translated file as a response
    return FileResponse(translated_path, filename=f"translated_{file.filename}", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")


if __name__ == "__main__": 
    uvicorn.run(app, host="0.0.0.0", port=8000)