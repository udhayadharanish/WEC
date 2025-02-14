import cv2
import numpy as np
from PIL import Image
import potrace
import io

def remove_background(image_path):
    # Load image
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply threshold to get binary mask
    _, mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create a new mask with transparent background
    new_mask = np.zeros_like(image, dtype=np.uint8)
    new_mask.fill(255)  # White background
    
    # Draw contours
    cv2.drawContours(new_mask, contours, -1, (0, 0, 0), thickness=cv2.FILLED)
    
    # Convert back to PIL for tracing
    pil_image = Image.fromarray(new_mask)
    return pil_image.convert("L")

def image_to_svg(image):
    # Convert image to bitmap
    bitmap = potrace.Bitmap(image)
    
    # Trace to create a path
    path = bitmap.trace()
    
    # Generate SVG
    svg_output = io.StringIO()
    svg_output.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">')
    
    for curve in path:
        svg_output.write("<path d='M")
        first = True
        for segment in curve:
            if first:
                svg_output.write(f"{segment.start_point[0]},{segment.start_point[1]} ")
                first = False
            svg_output.write("C" + " ".join(f"{p.x},{p.y}" for p in segment.c))
        svg_output.write("Z' fill='black'/>")
    
    svg_output.write('</svg>')
    return svg_output.getvalue()

def convert_icon_to_svg(image_path, output_svg):
    processed_image = remove_background(image_path)
    svg_data = image_to_svg(processed_image)
    
    with open(output_svg, "w") as f:
        f.write(svg_data)
    
    print(f"SVG saved at: {output_svg}")