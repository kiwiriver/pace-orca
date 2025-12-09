"""
simpler function used in testing
"""
import os
import base64
from PIL import Image
import numpy as np

def write_gallery_section_no_hidden(image_list, file_handle, sequence, titlev, resolution_factor=1, quality=85):
    """
    Write images from a section into a gallery following the provided sequence and custom titles.
    """
    valid_extensions = {".png", ".jpg", ".jpeg"}
    filtered_images = [img for img in image_list if is_valid_image(img, valid_extensions)]

    for row_idx, row in enumerate(sequence):
        file_handle.write("<div class='row'>\n")
        for col_idx, col_key in enumerate(row):
            matched_image = next((img for img in filtered_images if f"_{col_key}." in img), None)
            if matched_image:
                css_class = "small" if col_key == "globe" else "large"
                encoded_image = encode_image_to_base64(matched_image, factor=resolution_factor, quality=quality)
                caption = titlev[row_idx][col_idx] if titlev and titlev[row_idx][col_idx] else ""
                
                if encoded_image:
                    file_handle.write(f"<div class='img-container {css_class}'>\n")
                    file_handle.write(f"<img src='data:image/jpeg;base64,{encoded_image}' alt='{caption}' />\n")
                    file_handle.write(f"<div class='caption'>{caption}</div>\n</div>\n")
        file_handle.write("</div>\n")

def write_single_image(image, file_handle, resolution_factor=1, quality=85):
    """
    Write images from a section into a gallery following the provided sequence and custom titles.
    """
    encoded_image = encode_image_to_base64(image, factor=resolution_factor, quality=quality)
    css_class = "small"
    caption=''
    if encoded_image:
        file_handle.write("<div>\n")        
        file_handle.write(f"<div class='img-container {css_class}'>\n")
        file_handle.write(f"<img src='data:image/jpeg;base64,{encoded_image}' alt='{caption}' />\n")
        file_handle.write(f"<div class='caption'>{caption}</div>\n</div>\n")
        file_handle.write("</div>\n")