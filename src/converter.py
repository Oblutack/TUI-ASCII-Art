import logging
import ascii_magic
from PIL import Image
from typing import Union

def convert_image_to_ascii(image_source: Union[str, Image.Image], columns: int = 120):
    try:
        logging.info(f"Converter: Primio 'image_source' tipa: {type(image_source)}")
        
        art_object = ascii_magic.from_image(image_source)
        logging.info("Converter: Uspješno kreiran ascii_magic objekat.")
        
        ascii_art_string = art_object.to_terminal(columns=columns)
        logging.info("Converter: Uspješno generisan string za terminal.")
        
        return ascii_art_string
    except Exception as e:
        logging.exception(f"Converter: Desila se greška unutar ascii_magic biblioteke: {e}")
        return None