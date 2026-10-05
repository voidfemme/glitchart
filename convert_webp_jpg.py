
from PIL import Image
import sys
import os

def webp_to_jpg(input_path, output_path=None):
    """
    Converts a WebP image to a JPEG image using the Pillow library.
    
    :param input_path: Path to the input .webp file.
    :param output_path: Path to save the output .jpg file. If not provided, 
                        the .jpg file will be saved in the same folder 
                        with the same name as input_path, but with a .jpg extension.
    """
    # If no output path is specified, replace .webp with .jpg
    if not output_path:
        base, _ = os.path.splitext(input_path)
        output_path = base + ".jpg"
    
    # Open and convert to RGB (JPEG doesn't support alpha channels)
    image = Image.open(input_path).convert("RGB")
    
    # Save as JPEG
    image.save(output_path, "JPEG")
    print(f"Converted {input_path} to {output_path}")

if __name__ == "__main__":
    # Command-line usage example:
    # python webp_to_jpg.py input_file.webp output_file.jpg
    
    # Check if user provided the input file
    if len(sys.argv) < 2:
        print("Usage: python webp_to_jpg.py <input_file.webp> [output_file.jpg]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Check if output path is provided
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        output_file = None  # will auto-generate a .jpg file name
    
    webp_to_jpg(input_file, output_file)
