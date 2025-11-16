import ascii_magic
from PIL import Image

def convert_image_to_ascii(image_path: str, columns: int = 120):
    """
    Takes a path to an image and returns its colorful ASCII art representation.
    
    Args:
        image_path (str): The full path to the input image.
        columns (int): The width of the output ASCII art in characters.
        
    Returns:
        str: The generated ASCII art as a string, ready for printing.
    """
    try:
        art_object = ascii_magic.from_image(image_path)
        
        ascii_art_string = art_object.to_terminal(columns=columns)
        
        return ascii_art_string
        
    except FileNotFoundError:
        return f"Error: The file '{image_path}' was not found."
    except Exception as e:
        return f"An error occurred: {e}"