"""
Generate sample test images for image captioning demo.
Creates simple synthetic images for testing without requiring real datasets.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def generate_sample_images():
    """Generate sample test images"""
    
    os.makedirs('.', exist_ok=True)
    
    # Sample 1: Beach scene
    img1 = Image.new('RGB', (640, 480), color='#87CEEB')
    draw1 = ImageDraw.Draw(img1)
    # Sky
    draw1.rectangle([0, 0, 640, 300], fill='#87CEEB')
    # Sand
    draw1.rectangle([0, 300, 640, 480], fill='#F4A460')
    # Sun
    draw1.ellipse([500, 50, 600, 150], fill='#FFD700')
    img1.save('beach.jpg', 'JPEG')
    print("✓ Created beach.jpg")
    
    # Sample 2: Mountain scene
    img2 = Image.new('RGB', (640, 480), color='#87CEEB')
    draw2 = ImageDraw.Draw(img2)
    # Sky
    draw2.rectangle([0, 0, 640, 300], fill='#87CEEB')
    # Mountain
    draw2.polygon([(100, 300), (320, 100), (540, 300)], fill='#696969')
    # Ground
    draw2.rectangle([0, 300, 640, 480], fill='#228B22')
    img2.save('mountain.jpg', 'JPEG')
    print("✓ Created mountain.jpg")
    
    # Sample 3: City scene
    img3 = Image.new('RGB', (640, 480), color='#87CEEB')
    draw3 = ImageDraw.Draw(img3)
    # Sky
    draw3.rectangle([0, 0, 640, 240], fill='#87CEEB')
    # Buildings
    draw3.rectangle([100, 150, 200, 400], fill='#A9A9A9')
    draw3.rectangle([250, 100, 350, 400], fill='#808080')
    draw3.rectangle([400, 180, 500, 400], fill='#696969')
    # Ground
    draw3.rectangle([0, 400, 640, 480], fill='#708090')
    img3.save('city.jpg', 'JPEG')
    print("✓ Created city.jpg")
    
    # Sample 4: Nature scene
    img4 = Image.new('RGB', (640, 480), color='#87CEEB')
    draw4 = ImageDraw.Draw(img4)
    # Sky
    draw4.rectangle([0, 0, 640, 200], fill='#87CEEB')
    # Tree trunk
    draw4.rectangle([280, 200, 360, 400], fill='#8B4513')
    # Tree foliage
    draw4.ellipse([200, 100, 440, 300], fill='#228B22')
    # Ground
    draw4.rectangle([0, 400, 640, 480], fill='#90EE90')
    img4.save('tree.jpg', 'JPEG')
    print("✓ Created tree.jpg")
    
    print("\n✅ All sample images created successfully!")
    print("\nSample images:")
    for img in ['beach.jpg', 'mountain.jpg', 'city.jpg', 'tree.jpg']:
        if os.path.exists(img):
            size = os.path.getsize(img) / 1024
            print(f"  - {img} ({size:.1f} KB)")

if __name__ == "__main__":
    generate_sample_images()
