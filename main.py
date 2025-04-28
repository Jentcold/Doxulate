from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Depends
from fastapi.responses import HTMLResponse,JSONResponse,FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from pydantic import BaseModel
from datetime import datetime, timedelta
import uvicorn
import os
import shutil
import magic
import Functions

# Initialize FastAPI app
app = FastAPI()

# Set up the templates directory for Jinja2
templates = Jinja2Templates(directory="/app/site")

# Serve static files (CSS, JS, etc.)
app.mount("/site", StaticFiles(directory="/app/site"), name="HTML")
app.mount("/HomePageAssets", StaticFiles(directory="/app/site/HomePageAssets"), name="HomePageAssets")

# Set up for file transfer 
# Allowed file types (MIME types)
ALLOWED_FILE_TYPES = {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"}

# Max file size (10 MB) 
MAX_FILE_SIZE = 10 * 1024 * 1024  

# Temporary storage directory
UPLOAD_DIR = "/app/tmp"
TRANSLATED_DIR = "/app/tmp_translated"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TRANSLATED_DIR, exist_ok=True)

# clean temp_translated
def cleanup_old_files(folder_path="/temp_translated", max_age_hours=24):
    try:
        if not os.path.exists(folder_path):
            return
            
        now = datetime.now()
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if now - file_time > timedelta(hours=max_age_hours):
                    os.unlink(file_path)
                    print(f"Deleted old file: {filename}")
    except Exception as e:
        print(f"Cleanup error: {str(e)}")
        
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
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
