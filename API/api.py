import os
import shutil
import cv2
import numpy as np
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
SKETCH_DIR = os.path.join(MODEL_DIR, "processed_sketches")  # New directory for processed sketches
OUTPUT_DIR = os.path.join(MODEL_DIR, "generated_images")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(SKETCH_DIR, exist_ok=True)  # Create directory for processed sketches
os.makedirs(OUTPUT_DIR, exist_ok=True)

logger.info(f"Uploads directory: {UPLOAD_DIR}")
logger.info(f"Processed sketches directory: {SKETCH_DIR}")
logger.info(f"Generated images directory: {OUTPUT_DIR}")

# Mount the directories to serve files statically
app.mount("/images", StaticFiles(directory=OUTPUT_DIR), name="images")
app.mount("/sketches", StaticFiles(directory=SKETCH_DIR), name="sketches")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

def convert_to_sketch(image_path, output_path):
    """Convert an image to a sketch using edge detection."""
    try:
        # Read the image in grayscale
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
            
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        
        # Detect edges using Canny edge detector
        edges = cv2.Canny(blurred, 50, 150)
        
        # Invert the image to have black lines on white background if needed
        # edges = cv2.bitwise_not(edges)  # Uncomment if you need white lines on black background
        
        # Save the processed sketch
        cv2.imwrite(output_path, edges)
        logger.info(f"Sketch conversion successful: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error converting image to sketch: {str(e)}")
        return False

@app.post("/generate/")
async def generate_design(file: UploadFile = File(...)):
    try:
        # Generate a unique filename to avoid conflicts
        filename_parts = os.path.splitext(file.filename)
        unique_id = os.urandom(4).hex()
        
        # Save the original uploaded file
        original_filename = f"{filename_parts[0]}_{unique_id}_original{filename_parts[1]}"
        original_path = os.path.join(UPLOAD_DIR, original_filename)
        logger.info(f"Saving uploaded image to: {original_path}")
        
        with open(original_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Convert the uploaded image to a sketch (for processing purposes)
        sketch_filename = f"{filename_parts[0]}_{unique_id}_sketch.png"
        sketch_path = os.path.join(SKETCH_DIR, sketch_filename)
        logger.info(f"Converting image to sketch: {sketch_path}")
        
        success = convert_to_sketch(original_path, sketch_path)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to convert image to sketch")
        
        # Generate the image using the sketch
        logger.info(f"Generating image from sketch: {sketch_path}")
        output_path, processed_sketch_path = generate_image(
            sketch_path=sketch_path,
            output_dir=OUTPUT_DIR
        )
        
        # Log the output paths
        logger.info(f"Generated image path: {output_path}")
        
        # Get the filenames for the paths
        generated_image_filename = os.path.basename(output_path)
        
        # Verify files exist
        if not os.path.exists(output_path):
            logger.error(f"Generated image not found at: {output_path}")
            raise HTTPException(status_code=500, detail="Generated image not found")
        
        # Return the URLs - with original_sketch pointing to the ORIGINAL UPLOAD
        response_data = {
            "success": True,
            "generated_image": f"/images/{generated_image_filename}",
            "original_sketch": f"/uploads/{original_filename}",  # Changed to point to original upload
            # Include additional info but don't break existing frontend
            "additional_info": {
                "converted_sketch": f"/sketches/{sketch_filename}",
                "processed_sketch": f"/images/{os.path.basename(processed_sketch_path)}"
            }
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
        sketch_files = os.listdir(SKETCH_DIR)
        output_files = os.listdir(OUTPUT_DIR)
        
        return {
            "upload_dir": UPLOAD_DIR,
            "sketch_dir": SKETCH_DIR,
            "output_dir": OUTPUT_DIR,
            "upload_files": upload_files,
            "sketch_files": sketch_files,
            "output_files": output_files,
            "mount_points": ["/images", "/sketches", "/uploads"]
        }
    except Exception as e:
        logger.error(f"Error in test-paths: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info(f"Starting server with upload dir: {UPLOAD_DIR}")
    logger.info(f"Sketch dir: {SKETCH_DIR}")
    logger.info(f"Output dir: {OUTPUT_DIR}")
    logger.info(f"Model dir: {MODEL_DIR}")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)