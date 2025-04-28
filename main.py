import os
import shutil
import magic
import requests
time
import logging
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
import uvicorn
import Functions

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# === Define variables ===
# Allowed file types (MIME types)
ALLOWED_FILE_TYPES = {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
# Max file size (10 MB)
MAX_FILE_SIZE = 10 * 1024 * 1024
# Temporary storage directories
UPLOAD_DIR = "/app/tmp"
TRANSLATED_DIR = "/app/tmp_translated"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TRANSLATED_DIR, exist_ok=True)

# === Define functions ===
# Waiting function
def wait_for_service(url, timeout=60):
    start_time = time.time()
    while True:
        try:
            r = requests.get(url)
            if r.status_code == 200:
                logger.info(f"Service {url} is ready!")
                return
        except requests.exceptions.RequestException:
            pass
        if time.time() - start_time > timeout:
            logger.error(f"Timeout waiting for service {url}")
            raise Exception(f"Timeout waiting for service {url}")
        logger.info(f"Waiting for {url}...")
        time.sleep(2)

# Clean old translated files
def cleanup_old_files(folder_path=TRANSLATED_DIR, max_age_hours=24):
    try:
        if not os.path.exists(folder_path):
            return
        now = __import__('datetime').datetime.now()
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                file_time = __import__('datetime').datetime.fromtimestamp(os.path.getmtime(file_path))
                if now - file_time > __import__('datetime').timedelta(hours=max_age_hours):
                    os.unlink(file_path)
                    logger.info(f"Deleted old file: {filename}")
    except Exception as e:
        logger.error(f"Cleanup error: {e}")

# === Initialize APP ===
app = FastAPI()

# Wait for LibreTranslate at startup
def on_startup():
    try:
        wait_for_service("http://libretranslate:5000")
    except Exception as e:
        logger.error(f"Startup wait failed: {e}")
app.add_event_handler("startup", on_startup)

# Templates and static files
templates = Jinja2Templates(directory="/app/site")
app.mount("/site", StaticFiles(directory="/app/site"), name="site")
app.mount("/HomePageAssets", StaticFiles(directory="/app/site/HomePageAssets"), name="assets")

# Home page endpoint
@app.get("/", response_class=HTMLResponse)
def load_homepage(request: Request):
    return templates.TemplateResponse("homepage.html", {"request": request, "variable": "value"})

# File Upload endpoint
@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    source_lang: str = Form(...),
    target_lang: str = Form(...)
):
    cleanup_old_files()
    # Read and validate file
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        logger.warning("Uploaded file exceeds size limit")
        raise HTTPException(status_code=400, detail="File size exceeds the limit (10MB).")
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(file_content)
    if file_type not in ALLOWED_FILE_TYPES:
        logger.warning(f"Invalid file type: {file_type}")
        raise HTTPException(status_code=400, detail="Invalid file type. Only DOCX allowed.")

    file_path = os.path.join(UPLOAD_DIR, f"file_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(file_content)

    try:
        translated_path = Functions.full_operation(file_path, source_lang, target_lang)
        return FileResponse(translated_path, filename=f"translated_{file.filename}", media_type=file_type)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload processing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Removed temporary file: {file_path}")
        except Exception as e:
            logger.error(f"Error removing temp file: {e}")

# Run the app
if __name__ == "__main__":
    port = int(os.getenv('PORT', 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
