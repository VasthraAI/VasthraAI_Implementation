import os
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vasthra-api")

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

logger.info(f"Uploads directory: {UPLOAD_DIR}")
logger.info(f"Generated images directory: {OUTPUT_DIR}")

# Mount the directories to serve files statically
app.mount("/images", StaticFiles(directory=OUTPUT_DIR), name="images")
app.mount("/sketches", StaticFiles(directory=UPLOAD_DIR), name="sketches")

@app.post("/generate/")
async def generate_design(file: UploadFile = File(...)):
    try:
        # Generate a unique filename to avoid conflicts
        filename_parts = os.path.splitext(file.filename)
        unique_filename = f"{filename_parts[0]}_{os.urandom(4).hex()}{filename_parts[1]}"
        
        # Save the uploaded file
        sketch_path = os.path.join(UPLOAD_DIR, unique_filename)
        logger.info(f"Saving uploaded sketch to: {sketch_path}")
        
        with open(sketch_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Generate the image using your existing generate_image function
        logger.info(f"Generating image from sketch: {sketch_path}")
        output_path, sketch_output_path = generate_image(
            sketch_path=sketch_path,
            output_dir=OUTPUT_DIR
        )
        
        # Log the output paths
        logger.info(f"Generated image path: {output_path}")
        logger.info(f"Processed sketch path: {sketch_output_path}")
        
        # Get the filenames for the paths
        generated_image_filename = os.path.basename(output_path)
        sketch_filename = os.path.basename(sketch_output_path)
        
        # Verify files exist
        if not os.path.exists(output_path):
            logger.error(f"Generated image not found at: {output_path}")
        
        if not os.path.exists(sketch_output_path):
            logger.error(f"Processed sketch not found at: {sketch_output_path}")
        
        # Return the URLs to access these files
        response_data = {
            "success": True,
            "generated_image": f"/images/{generated_image_filename}",
            "original_sketch": f"/images/{sketch_filename}"  # Changed to images directory!
        }
        
        logger.info(f"Response data: {response_data}")
        return response_data
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-paths")
async def test_paths():
    """Endpoint to test if directories are accessible"""
    try:
        upload_files = os.listdir(UPLOAD_DIR)
        output_files = os.listdir(OUTPUT_DIR)
        
        return {
            "upload_dir": UPLOAD_DIR,
            "output_dir": OUTPUT_DIR,
            "upload_files": upload_files,
            "output_files": output_files,
            "mount_points": ["/images", "/sketches"]
        }
    except Exception as e:
        logger.error(f"Error in test-paths: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info(f"Starting server with upload dir: {UPLOAD_DIR}")
    logger.info(f"Output dir: {OUTPUT_DIR}")
    logger.info(f"Model dir: {MODEL_DIR}")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)