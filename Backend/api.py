from fastapi import FastAPI, File, UploadFile
import os
import subprocess
from fastapi.responses import FileResponse
import shutil

app = FastAPI()

# Define paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_DIR = os.path.join(BASE_DIR, "Model")
UPLOAD_DIR = os.path.join(MODEL_DIR, "uploaded_sketches")
OUTPUT_DIR = os.path.join(MODEL_DIR, "generated_images")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/generate/")
async def generate_image(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save the uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run the GAN model script
    command = f'python "{os.path.join(MODEL_DIR, "generate_image.py")}" --sketch_path "{file_path}"'
    subprocess.run(command, shell=True)

    # Find the latest generated image
    generated_files = sorted(os.listdir(OUTPUT_DIR), key=lambda f: os.path.getctime(os.path.join(OUTPUT_DIR, f)))
    if not generated_files:
        return {"error": "No image generated"}

    generated_image_filename = generated_files[-1]
    return {"generated_image": generated_image_filename}

@app.get("/generated-image/{filename}")
async def get_generated_image(filename: str):
    return FileResponse(os.path.join(OUTPUT_DIR, filename))

