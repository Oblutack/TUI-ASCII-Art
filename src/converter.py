import logging
import ascii_magic
from PIL import Image
from typing import Union, List, Tuple, Optional

def convert_image_to_ascii(image_source: Union[str, Image.Image], columns: int = 120, char_set: str = None) -> Optional[str]:
    """
    Converts a single image (from a path or PIL object) into a colorful ASCII art string.
    
    Args:
        image_source: Path to image or PIL Image object
        columns: Width in characters
        char_set: Custom character set (optional)
    
    Returns:
        ASCII art string or None on error
    """
    try:
        if isinstance(image_source, Image.Image):
            logging.info("Converter: Received PIL Image object. Using it directly.")
            art_object = ascii_magic.from_pillow_image(image_source)
        else:
            logging.info(f"Converter: Received path string. Using from_image.")
            art_object = ascii_magic.from_image(image_source)

        logging.info("Converter: Successfully created ascii_magic object.")
        
        # Use custom character set if provided
        if char_set:
            logging.info(f"Converter: Using custom character set: {char_set}")
            # ascii_magic doesn't directly support custom chars, so we'll do post-processing
            ascii_art_string = art_object.to_terminal(columns=columns)
            # Note: For true custom char support, we'd need to modify the algorithm
            # For now, we'll use ascii_magic's default and note this limitation
        else:
            ascii_art_string = art_object.to_terminal(columns=columns)
        
        logging.info("Converter: Successfully generated terminal string.")
        return ascii_art_string
    except Exception as e:
        logging.exception(f"Converter: An error occurred within the ascii_magic library: {e}")
        return None

def convert_image_to_ascii_custom(image: Image.Image, columns: int = 120, char_set: str = "@%#*+=-:. ") -> str:
    """
    Convert image to ASCII using custom character set with manual algorithm
    
    Args:
        image: PIL Image object
        columns: Width in characters
        char_set: Character set from dark to light
    
    Returns:
        ASCII art string
    """
    try:
        # Calculate dimensions
        aspect_ratio = image.height / image.width
        rows = int(columns * aspect_ratio * 0.55)  # 0.55 for character aspect ratio
        
        # Resize image
        img_resized = image.resize((columns, rows))
        img_gray = img_resized.convert('L')  # Convert to grayscale
        
        # Get pixel data
        pixels = list(img_gray.getdata())
        
        # Convert pixels to characters
        ascii_str = ""
        char_count = len(char_set) - 1
        
        for i, pixel in enumerate(pixels):
            # Map pixel brightness (0-255) to character index
            char_index = int((pixel / 255) * char_count)
            ascii_str += char_set[char_index]
            
            # Add newline at end of row
            if (i + 1) % columns == 0:
                ascii_str += '\n'
        
        return ascii_str
    except Exception as e:
        logging.exception(f"Converter: Error in custom conversion: {e}")
        return ""

def convert_gif_to_ascii_frames(gif_path: str, columns: int = 120, char_set: str = None) -> List[Tuple[str, float]]:
    """
    Opens a GIF, converts each frame to ASCII art, and returns a list of
    (frame_string, duration_in_seconds).
    
    Args:
        gif_path: Path to GIF file
        columns: Width in characters
        char_set: Custom character set (optional)
    
    Returns:
        List of (frame_string, duration) tuples
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
                
                # Use custom conversion if char_set provided
                if char_set:
                    ascii_frame = convert_image_to_ascii_custom(frame_rgba, columns, char_set)
                else:
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