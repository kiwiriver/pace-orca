import os
import base64
from PIL import Image  # Ensure you have Pillow installed (`pip install Pillow`)


def is_valid_image(file_path, valid_extensions=None):
    """
    Checks if a file is a valid image file.
    """
    if valid_extensions is None:
        valid_extensions = {".png", ".jpg", ".jpeg"}
    return os.path.isfile(file_path) and os.path.splitext(file_path.lower())[1] in valid_extensions


def resize_and_compress_image(image_path, factor, output_format="JPEG", quality=85):
    """
    Resize the image based on a reduction factor and compress it to reduce file size.
    Uses Image.Resampling.LANCZOS instead of deprecated Image.ANTIALIAS.
    """
    try:
        with Image.open(image_path) as img:
            # Calculate new dimensions
            new_width = max(1, img.width // factor)
            new_height = max(1, img.height // factor)
            print(f"Original size: {img.width}x{img.height}, New size: {new_width}x{new_height}")

            # Resize the image (use Image.Resampling.LANCZOS for high-quality downscaling)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Save the resized image as compressed data
            from io import BytesIO
            buffer = BytesIO()
            img.convert("RGB").save(buffer, format=output_format, quality=quality)  # Compress
            compressed_size = len(buffer.getvalue())
            print(f"Compressed image size: {compressed_size} bytes")
            return buffer.getvalue()
    except Exception as e:
        print(f"❌ Error resizing and compressing image '{image_path}': {e}")
        return None


def encode_image_to_base64(image_path, factor=1, output_format="JPEG", quality=85):
    """
    Encodes an image to a Base64 string, optionally resizing and compressing it first.
    """
    try:
        if factor > 1:  # Resize and compress the image if a factor is specified
            compressed_image_data = resize_and_compress_image(image_path, factor, output_format, quality)
            if compressed_image_data is None:
                return None
            return base64.b64encode(compressed_image_data).decode("utf-8")
        else:  # No resizing or compressing, read the original file
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode("utf-8")
    except Exception as e:
        print(f"❌ Error encoding image '{image_path}': {e}")
        return None


def sort_images_by_sequence(image_list, sequence):
    """
    Sorts images based on a provided sequence of keys.

    Parameters:
    ----------
    image_list : list of str
        List of image file paths.
    sequence : list of list
        Sequence of image keys to determine the arrangement of rows and columns.

    Returns:
    -------
    list of list
        Sorted list of images arranged into rows and columns according to the sequence.
    """
    # Create a lookup table for image paths using the key in the file name
    image_dict = {}
    for img in image_list:
        base_name = os.path.basename(img)
        key = os.path.splitext(base_name)[0].split("_")[-1]  # Extract key from '_key.png'
        image_dict[key] = img

    # Reorder images based on the sequence
    ordered_images = []
    for row in sequence:
        ordered_row = [image_dict[key] for key in row if key in image_dict]
        ordered_images.append(ordered_row)

    return ordered_images


def make_html_gallery_embedded(image_list, html_out, sequence, \
                                    titlev=None, shrink_key="globe", title="Image Gallery", \
                                    resolution_factor=1, quality=85):
    """
    Create an HTML page that embeds PNG images as Base64 strings, arranged
    in rows and columns according to a sequence, with optional custom titles.
    Compresses and resizes images to reduce the HTML file size.

    Parameters:
    ----------
    image_list : list of str
        List of image file paths.
    html_out : str
        Path to the output HTML file.
    sequence : list of list
        Sequence that defines the arrangement of rows and columns by their keys.
    titlev : list of list or None, optional
        Titles for each image, matching the arrangement in the sequence. If None, file names will be used.
    shrink_key : str, optional
        Key for the image that should be shrunk in size. Default is "globe".
    title : str, optional
        Title of the HTML page.
    resolution_factor : int, optional
        Factor by which to reduce the resolution of the images. Default is 1 (no resizing).
    quality : int, optional
        Quality of the compressed image (for lossy formats like JPEG). Higher means better quality.
    """
    valid_extensions = {".png", ".jpg", ".jpeg"}
    # Filter out invalid images
    valid_images = [img for img in image_list if is_valid_image(img, valid_extensions)]
    if not valid_images:
        print("❌ No valid images found. Exiting.")
        return

    # Sort images according to the sequence
    ordered_images = sort_images_by_sequence(valid_images, sequence)

    with open(html_out, "w") as f:
        f.write("<!DOCTYPE html>\n<html>\n<head>\n")
        f.write("<meta charset='UTF-8'>\n")
        f.write(f"<title>{title}</title>\n")
        f.write("<style>\n")
        f.write("body { font-family: Arial, sans-serif; margin: 20px; }\n")
        f.write(".gallery { display: flex; flex-direction: column; gap: 20px; }\n")
        f.write(".row { display: flex; justify-content: center; gap: 20px; }\n")
        f.write(".small { flex: 1; } /* Small image */\n")
        f.write(".large { flex: 2; } /* Large image */\n")
        f.write(".img-container { display: flex; flex-direction: column; align-items: center; border: 1px solid #ccc; ")
        f.write("padding: 10px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); background-color: #fafafa; }\n")
        f.write(".img-container img { width: 100%; height: auto; display: block; border-radius: 5px; }\n")
        f.write(".caption { margin-top: 10px; font-weight: bold; text-align: center; }\n")
        f.write("</style>\n</head>\n<body>\n")
        f.write(f"<h1>{title}</h1>\n")
        f.write("<div class='gallery'>\n")

        # Write rows of images
        for row_idx, row in enumerate(ordered_images):
            f.write("<div class='row'>\n")
            for col_idx, img in enumerate(row):
                # Determine title: use titlev if provided, fall back to default file name
                if titlev and row_idx < len(titlev) and col_idx < len(titlev[row_idx]):
                    caption = titlev[row_idx][col_idx]
                else:
                    caption = os.path.splitext(os.path.basename(img))[0]  # Default to file name

                # Check if the image matches the shrink_key
                css_class = "small" if shrink_key in img else "large"

                # Encode and compress the image
                encoded = encode_image_to_base64(img, factor=resolution_factor, output_format="JPEG", quality=quality)
                if not encoded:
                    continue
                f.write(f"<div class='img-container {css_class}'>\n")
                f.write(f"<img src='data:image/jpeg;base64,{encoded}' alt='{caption}'>\n")
                f.write(f"<div class='caption'>{caption}</div>\n")
                f.write("</div>\n")
            f.write("</div>\n")

        f.write("</div>\n</body>\n</html>\n")

    print(f"✅ HTML gallery written to: {html_out}")


# Example Usage:
# image_list = [
#     "path/to/image_rgb.png", "path/to/image_globe.png", "path/to/image_aot.png",
#     "path/to/image_ssa.png", "path/to/image_fvf.png", "path/to/image_sph.png"
# ]

# sequence = [['rgb', 'globe', 'aot'], ['ssa', 'fvf', 'sph']]
# titlev = [["RGB Image", "Globe Image", "AOD 550nm"], ["SSA", "FVF", "SPH"]]
# make_html_gallery_embedded(image_list, "output.html", sequence, titlev, resolution_factor=4, quality=70)