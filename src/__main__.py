from .converter import convert_image_to_ascii
import os

def main():
    from PIL import Image, ImageDraw

    test_image_path = "test_image.png"

    if not os.path.exists(test_image_path):
        print(f"Creating a test image at '{test_image_path}'...")
        img = Image.new('RGB', (200, 150), color = 'red')
        d = ImageDraw.Draw(img)
        d.rectangle([40, 30, 160, 120], fill='yellow', outline='blue', width=5)
        d.text((55, 65), "ASCII Test!", fill='black')
        img.save(test_image_path)

    print("--- CONVERTING IMAGE TO ASCII ART ---")
    ascii_result = convert_image_to_ascii(test_image_path)
    
    print(ascii_result)
    print("-------------------------------------")

if __name__ == "__main__":
    main()