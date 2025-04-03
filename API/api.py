import os
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

# Determine the root directory of the project
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(ROOT_DIR, "Model")

# Add Model directory to Python path
import sys
sys.path.append(MODEL_DIR)  # Add Model directory to Python path

# Import your GAN function
from generate_image import generate_image

app = FastAPI(title="VasthraAI API")

# Add CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories with absolute paths
UPLOAD_DIR = os.path.join(MODEL_DIR, "uploaded_sketches")
OUTPUT_DIR = os.path.join(MODEL_DIR, "generated_images")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mount the directories to serve files statically
app.mount("/images", StaticFiles(directory=OUTPUT_DIR), name="images")
app.mount("/sketches", StaticFiles(directory=UPLOAD_DIR), name="sketches")

@app.post("/generate/")
async def generate_design(file: UploadFile = File(...)):
    try:
        # Save the uploaded file
        sketch_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(sketch_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Generate the image using your existing generate_image function
        output_path, sketch_output_path = generate_image(
            sketch_path=sketch_path,
            output_dir=OUTPUT_DIR
        )
        
        # Get the filenames for the paths
        generated_image_filename = os.path.basename(output_path)
        sketch_filename = os.path.basename(sketch_output_path)
        
        # Return the URLs to access these files
        return {
            "success": True,
            "generated_image": f"/images/{generated_image_filename}",
            "original_sketch": f"/sketches/{sketch_filename}"
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print(f"Starting server with upload dir: {UPLOAD_DIR}")
    print(f"Output dir: {OUTPUT_DIR}")
    print(f"Model dir: {MODEL_DIR}")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)