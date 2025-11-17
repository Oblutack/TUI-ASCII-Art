import logging
from rembg import remove
from PIL import Image

def remove_background_from_image(input_path: str) -> Image.Image:
    try:
        logging.info(f"Rembg: Otvaram sliku sa putanje: {input_path}")
        with Image.open(input_path) as img:
            logging.info("Rembg: Slika uspješno otvorena. Započinjem uklanjanje pozadine...")
            output_image = remove(img)
            logging.info(f"Rembg: Pozadina uspješno uklonjena. Vraćam PIL Image objekat tipa: {type(output_image)}")
            return output_image
    except Exception as e:
        logging.exception(f"Došlo je do katastrofalne greške unutar REMBG biblioteke: {e}")
        return None