import logging
import ascii_magic
from PIL import Image
from typing import Union, List, Tuple, Optional

def convert_image_to_ascii(image_source: Union[str, Image.Image], columns: int = 120) -> Optional[str]:
    """
    Converts a single image (from a path or PIL object) into a colorful ASCII art string.
    """
    try:
        if isinstance(image_source, Image.Image):
            logging.info("Converter: Received PIL Image object. Using it directly.")
            art_object = ascii_magic.from_pillow_image(image_source)
        else:
            logging.info(f"Converter: Received path string. Using from_image.")
            art_object = ascii_magic.from_image(image_source)

        logging.info("Converter: Successfully created ascii_magic object.")
        ascii_art_string = art_object.to_terminal(columns=columns)
        logging.info("Converter: Successfully generated terminal string.")
        return ascii_art_string
    except Exception as e:
        logging.exception(f"Converter: An error occurred within the ascii_magic library: {e}")
        return None

def convert_gif_to_ascii_frames(gif_path: str, columns: int = 120) -> List[Tuple[str, float]]:
    """
    Opens a GIF, converts each frame to ASCII art, and returns a list of
    (frame_string, duration_in_seconds).
    """
    frames = []
    try:
        with Image.open(gif_path) as gif:
            frame_index = 0
            while True:
                logging.info(f"Converter (GIF): Processing frame {frame_index}...")
                gif.seek(frame_index)
                duration_ms = gif.info.get('duration', 100)
                duration_s = duration_ms / 1000.0
                
                frame_rgba = gif.convert('RGBA')
                
                ascii_frame = convert_image_to_ascii(frame_rgba, columns=columns)
                
                if ascii_frame:
                    frames.append((ascii_frame, duration_s))
                
                frame_index += 1
    except EOFError:
        logging.info(f"Converter (GIF): Reached end of GIF after {len(frames)} frames.")
        pass
    except Exception as e:
        logging.exception(f"Converter (GIF): An error occurred while processing the GIF: {e}")

    return frames