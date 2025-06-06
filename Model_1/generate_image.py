import torch
from torchvision import transforms
from PIL import Image
import os
from datetime import datetime
import argparse
import numpy as np
import cv2  # Add OpenCV import

# Dynamic import based on generator number
def load_generator_module(generator_num):
    if generator_num == 2:
        from sketch_to_image_gan_2 import Generator
    else:
        from sketch_to_image_gan import Generator
    return Generator

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Get the absolute path to the model directory
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))

# Define image transformations (same as training)
transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),  # Ensure single-channel input
    transforms.Resize((512, 512)),  # Match training size
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5])  # Normalize to [-1, 1]
])

def preprocess_sketch(sketch_path):
    """Apply preprocessing to enhance sketch quality before generation using OpenCV."""
    # Load the image using OpenCV in grayscale
    image = cv2.imread(sketch_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Failed to load image at {sketch_path}")

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(image, (5, 5), 0)

    # Detect edges using Canny
    edges = cv2.Canny(blurred, 50, 150)

    # Optional: Enhance contrast further (if needed)
    edges = np.clip((edges.astype(np.float32) - 128) * 1.5 + 128, 0, 255).astype(np.uint8)

    # Convert back to PIL Image
    enhanced_sketch = Image.fromarray(edges)

    return enhanced_sketch

def generate_image(sketch_path, output_dir="generated_images", enhance_sketch=True, ensemble=True, generator_num=1):
    """Generate an image from a sketch with optional enhancements."""
    # Make output_dir absolute if it's relative
    if not os.path.isabs(output_dir):
        output_dir = os.path.join(MODEL_DIR, output_dir)
        
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Load the specified generator model
    Generator = load_generator_module(generator_num)
    generator = Generator().to(device)
    generator_path = os.path.join(MODEL_DIR, f"generator_{generator_num}.pth")
    
    # Check if the generator file exists
    if not os.path.exists(generator_path):
        raise FileNotFoundError(f"Generator model not found: {generator_path}")
    
    generator.load_state_dict(torch.load(generator_path, map_location=device))
    generator.eval()

    # Generate the timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create the output file path with the timestamp
    output_filename = f"generated_image_{timestamp}.png"
    output_path = os.path.join(output_dir, output_filename)
    
    # Save original sketch for comparison
    sketch_output_path = os.path.join(output_dir, f"input_sketch_{timestamp}.png")
    
    # Preprocess the sketch if enhancement is enabled
    if enhance_sketch:
        sketch = preprocess_sketch(sketch_path)
        sketch.save(sketch_output_path)
    else:
        sketch = Image.open(sketch_path).convert("L")
        sketch.save(sketch_output_path)
    
    # Transform the sketch
    sketch_tensor = transform(sketch).unsqueeze(0).to(device)
    
    # Generate with ensemble if enabled (average multiple generations with small noise)
    if ensemble:
        with torch.no_grad():
            # Generate multiple versions with noise and average them
            num_samples = 3
            generated_images = []
            
            for _ in range(num_samples):
                # Add small noise to sketch input
                noise = torch.randn_like(sketch_tensor) * 0.02
                noisy_sketch = sketch_tensor + noise
                
                # Generate image
                gen_img = generator(noisy_sketch)
                generated_images.append(gen_img)
            
            # Average the generated images
            generated_image = torch.mean(torch.stack(generated_images), dim=0)
    else:
        # Single generation
        with torch.no_grad():
            generated_image = generator(sketch_tensor)

    # Post-process: Convert output tensor to image
    generated_image = (generated_image.squeeze(0).permute(1, 2, 0).cpu().numpy() + 1) / 2  # Convert to [0,1]
    generated_image = (generated_image * 255).astype("uint8")  # Convert to uint8

    # Save the image
    Image.fromarray(generated_image).save(output_path)
    print(f"Generated image saved at: {output_path}")
    print(f"Input sketch saved at: {sketch_output_path}")
    
    return output_path, sketch_output_path

# Parse command-line arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate an image from a sketch.")
    parser.add_argument(
        "--sketch_path",
        type=str,
        required=True,
        help="Path to the input sketch image."
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="generated_images",
        help="Directory to save the generated image. Default is 'generated_images'."
    )
    parser.add_argument(
        "--enhance",
        action='store_true',
        help="Apply sketch enhancement preprocessing."
    )
    parser.add_argument(
        "--ensemble",
        action='store_true',
        help="Use ensemble generation for better results."
    )
    parser.add_argument(
        "--generator_num",
        type=int,
        default=1,
        choices=[1, 2, 3],
        help="Generator model to use (1, 2, or 3)."
    )
    args = parser.parse_args()

    # Generate the image
    generate_image(args.sketch_path, args.output_dir, args.enhance, args.ensemble, args.generator_num)