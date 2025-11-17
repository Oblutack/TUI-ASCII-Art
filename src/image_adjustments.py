"""
Image Adjustments Module
Applies brightness, contrast, and color adjustments to images before ASCII conversion
"""

from PIL import Image, ImageEnhance, ImageOps
import logging


class ImageAdjustments:
    """Handles image preprocessing adjustments"""
    
    @staticmethod
    def adjust_brightness(image: Image.Image, brightness: int) -> Image.Image:
        """
        Adjust image brightness
        
        Args:
            image: PIL Image
            brightness: Brightness value (-100 to +100, 0 = no change)
        
        Returns:
            Adjusted image
        """
        if brightness == 0:
            return image
        
        try:
            # Convert brightness from -100/+100 to PIL's 0-2 scale
            # -100 = 0 (black), 0 = 1 (original), +100 = 2 (brighter)
            factor = 1.0 + (brightness / 100.0)
            factor = max(0.0, min(2.0, factor))  # Clamp between 0 and 2
            
            enhancer = ImageEnhance.Brightness(image)
            return enhancer.enhance(factor)
        except Exception as e:
            logging.error(f"Error adjusting brightness: {e}")
            return image
    
    @staticmethod
    def adjust_contrast(image: Image.Image, contrast: int) -> Image.Image:
        """
        Adjust image contrast
        
        Args:
            image: PIL Image
            contrast: Contrast value (25 to 200, 100 = no change)
                     25 = 0.25x, 100 = 1.0x, 200 = 2.0x
        
        Returns:
            Adjusted image
        """
        if contrast == 100:
            return image
        
        try:
            # Convert from percentage to factor
            factor = contrast / 100.0
            factor = max(0.25, min(2.0, factor))  # Clamp between 0.25 and 2.0
            
            enhancer = ImageEnhance.Contrast(image)
            return enhancer.enhance(factor)
        except Exception as e:
            logging.error(f"Error adjusting contrast: {e}")
            return image
    
    @staticmethod
    def invert_colors(image: Image.Image) -> Image.Image:
        """
        Invert image colors (negative effect)
        
        Args:
            image: PIL Image
        
        Returns:
            Inverted image
        """
        try:
            # Convert to RGB if needed
            if image.mode == 'RGBA':
                # Preserve alpha channel
                rgb = image.convert('RGB')
                inverted_rgb = ImageOps.invert(rgb)
                # Restore alpha
                inverted = Image.new('RGBA', image.size)
                inverted.paste(inverted_rgb)
                inverted.putalpha(image.split()[3])  # Copy alpha channel
                return inverted
            elif image.mode == 'RGB':
                return ImageOps.invert(image)
            else:
                # Convert to RGB first
                rgb = image.convert('RGB')
                return ImageOps.invert(rgb)
        except Exception as e:
            logging.error(f"Error inverting colors: {e}")
            return image
    
    @staticmethod
    def apply_all_adjustments(
        image: Image.Image,
        brightness: int = 0,
        contrast: int = 100,
        invert: bool = False
    ) -> Image.Image:
        """
        Apply all adjustments to image
        
        Args:
            image: PIL Image
            brightness: Brightness adjustment (-100 to +100)
            contrast: Contrast adjustment (25 to 200)
            invert: Whether to invert colors
        
        Returns:
            Adjusted image
        """
        result = image.copy()
        
        # Apply in order: brightness -> contrast -> invert
        if brightness != 0:
            result = ImageAdjustments.adjust_brightness(result, brightness)
        
        if contrast != 100:
            result = ImageAdjustments.adjust_contrast(result, contrast)
        
        if invert:
            result = ImageAdjustments.invert_colors(result)
        
        return result
    
    @staticmethod
    def get_adjustment_preview_text(brightness: int, contrast: int, invert: bool) -> str:
        """
        Get text description of current adjustments
        
        Args:
            brightness: Brightness value
            contrast: Contrast value
            invert: Invert enabled
        
        Returns:
            Description string
        """
        adjustments = []
        
        if brightness != 0:
            sign = "+" if brightness > 0 else ""
            adjustments.append(f"Bright: {sign}{brightness}")
        
        if contrast != 100:
            adjustments.append(f"Contrast: {contrast}%")
        
        if invert:
            adjustments.append("Inverted")
        
        if not adjustments:
            return "No adjustments"
        
        return " | ".join(adjustments)