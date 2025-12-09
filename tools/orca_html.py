"""
Put images into a html page, which can be shared through FILE_SHARE

Meng Gao, Sep 25, 2025

Images are embeded into the html page. 
Use resolution and image quality to adjust file size.
"""

import os
import base64
from PIL import Image
import numpy as np

def is_valid_image(file_path, valid_extensions=None):
    """
    Check if the file is a valid image.
    """
    if valid_extensions is None:
        valid_extensions = {".png", ".jpg", ".jpeg"}
    return os.path.isfile(file_path) and os.path.splitext(file_path.lower())[1] in valid_extensions


def resize_and_compress_image(image_path, factor, output_format="JPEG", quality=85):
    """
    Resize and compress the image to reduce file size.
    """
    try:
        with Image.open(image_path) as img:
            new_width = max(1, img.width // factor)
            new_height = max(1, img.height // factor)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Save the resized image as compressed data
            from io import BytesIO
            buffer = BytesIO()
            img.convert("RGB").save(buffer, format=output_format, quality=quality)
            return buffer.getvalue()
    except Exception as e:
        print(f"❌ Error resizing/compressing image '{image_path}': {e}")
        return None


def encode_image_to_base64(image_path, factor=1, output_format="JPEG", quality=85):
    """
    Encode an image to a Base64 string, optionally resizing/compressing it first.
    """
    try:
        if factor > 1:
            compressed_data = resize_and_compress_image(image_path, factor, output_format, quality)
            if compressed_data:
                return base64.b64encode(compressed_data).decode("utf-8")
        else:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode("utf-8")
    except Exception as e:
        print(f"❌ Error encoding image '{image_path}': {e}")
        return None


def get_images_from_subfolders(base_folder, valid_extensions=None):
    """
    Collect images from all subdirectories (timestamps).
    """
    if valid_extensions is None:
        valid_extensions = {".png", ".jpg", ".jpeg"}

    grouped_images = []
    for folder_name in sorted(os.listdir(base_folder)):
        folder_path = os.path.join(base_folder, folder_name)
        if os.path.isdir(folder_path):
            images = [os.path.join(folder_path, img) for img in sorted(os.listdir(folder_path))
                      if is_valid_image(os.path.join(folder_path, img), valid_extensions)]
            if images:
                grouped_images.append({"timestamp": folder_name, "images": images})
    return grouped_images

def convert_text_to_paragraphs(text):
        """
        Convert text with \n into HTML paragraphs (<p> tags).
        
        Args:
            text (str): The input text containing \n as line breaks.

        Returns:
            str: The text split into <p> tags for use in HTML.
        """
        if not text:
            return "<p>No message available</p>"
        
        paragraphs = text.split("\n")
        return "\n".join(f"<p>{line.strip()}</p>" for line in paragraphs if line.strip())  # Skip empty lines

def write_global_map_with_navigation(f, image_groups, infov_dict=None, global_map=None):
    """Write global map with bounding boxes and timestamp navigation box side by side."""
    
    # Start flex container
    f.write("""
    <div style="display: flex; flex-wrap: wrap; align-items: flex-start; margin-bottom: 20px; gap: 20px;">
    """)
    
    # Map container with title - takes more space
    f.write("""
    <div style="flex: 3; min-width: 300px;">
      <h3 style="margin-top: 0; color: #333;">Selected Scenes (Click on map to navigate)</h3>
    """)
    
    # Insert the map
    if infov_dict:
        write_global_map_with_bboxes(f, infov_dict=infov_dict, global_map=global_map)
    
    f.write("</div>")
    
    # Timestamp navigation box - takes less space
    f.write("""
    <div style="flex: 1; min-width: 200px;">
      <h3 style="margin-top: 0; color: #333;">Timestamp List of Selected Scenes</h3>
      <nav style="border:1px solid #ccc; border-radius:8px; 
                max-height:400px; overflow-y:auto; padding:10px; background-color:#f9f9f9;">
        <ul style="list-style:none; padding-left:0; margin:0; line-height:1.6;">
    """)
    
    for group in image_groups:
        f.write(f"""  <li><a href='#{group['timestamp']}' style='text-decoration:none; color:#0077cc;
                    display:block; padding:5px; border-radius:4px;'
                    onmouseover="this.style.backgroundColor='#e6f7ff';" 
                    onmouseout="this.style.backgroundColor='transparent';">
                    {group['timestamp']}</a></li>\n""")
    
    f.write("""
        </ul>
      </nav>
    </div>
    """)
    
    # Close flex container
    f.write("</div>")

# Replace the original separate navigation box and map with the combined function

def write_global_map_with_bboxes(
    file_handle,
    infov_dict=None,
    global_map=None,
    resolution_factor=1,
    quality=85,
    map_id="global-map",
    edge={'left': -34, 'right': -34, 'top': 10, 'bottom': 5}
):
    """
    Write a global map with clickable bounding boxes (SVG overlay).
    Handles dateline crossing for both rectangular and polygonal boxes.

    Parameters
    ----------
    file_handle : HTML file handle
    infov_dict : dict
        Example:
        {
          '20250301': {'boundingbox': [[lat1, lat2, ...], [lon1, lon2, ...]]}
        }
    """
    import numpy as np

    # --- Base map ---
    if global_map:
        encoded_image = encode_image_to_base64(global_map, factor=resolution_factor, quality=quality)
        map_tag = f"<img src='data:image/jpeg;base64,{encoded_image}' alt='Global Map' style='width:100%; display:block;'>"
    else:
        map_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/World_map_-_low_resolution.svg/1200px-World_map_-_low_resolution.svg.png"
        map_tag = f"<img src='{map_url}' alt='Global Map' style='width:100%; display:block;'>"

    file_handle.write(f"<div id='{map_id}' style='position:relative; display:inline-block; max-width:100%;'>\n")
    file_handle.write(map_tag + "\n")

    # --- SVG overlay ---
    if infov_dict:
        file_handle.write("<svg viewBox='0 0 100 100' style='position:absolute; top:0; left:0; width:100%; height:100%;'>\n")

        for ts, info in infov_dict.items():
            if "boundingbox" not in info:
                continue

            lats = np.array(info["boundingbox"][0])
            lons = np.array(info["boundingbox"][1])

            # --- POLYGONAL CASE ---
            if len(lats) >= 3 and len(lats) == len(lons):
                # Check for dateline crossing
                crosses = np.ptp(lons) > 180

                if crosses:
                    # Normalize to [-180, 180]
                    lons = np.where(lons > 180, lons - 360, lons)

                    # Split into two halves by longitude sign
                    east_mask = lons >= 0
                    west_mask = lons < 0

                    lon_east, lat_east = lons[east_mask], lats[east_mask]
                    lon_west, lat_west = lons[west_mask], lats[west_mask]

                    # Ensure non-empty parts
                    lon_parts, lat_parts = [], []

                    if len(lon_east) > 0:
                        # Close east polygon near +180
                        lat_top, lat_bottom = np.max(lat_east), np.min(lat_east)
                        lon_east_closed = np.concatenate(([180, 180], lon_east, [180, 180]))
                        lat_east_closed = np.concatenate(([lat_bottom, lat_top], lat_east, [lat_top, lat_bottom]))
                        lon_parts.append(lon_east_closed)
                        lat_parts.append(lat_east_closed)

                    if len(lon_west) > 0:
                        # Close west polygon near -180
                        lat_top, lat_bottom = np.max(lat_west), np.min(lat_west)
                        lon_west_closed = np.concatenate(([-180, -180], lon_west, [-180, -180]))
                        lat_west_closed = np.concatenate(([lat_bottom, lat_top], lat_west, [lat_top, lat_bottom]))
                        lon_parts.append(lon_west_closed)
                        lat_parts.append(lat_west_closed)
                else:
                    lon_parts = [lons]
                    lat_parts = [lats]

                # Draw polygons
                for lons_sub, lats_sub in zip(lon_parts, lat_parts):
                    points = []
                    for lat, lon in zip(lats_sub, lons_sub):
                        x = edge['left'] + (lon + 180) / 360 * (100 - edge['left'] - edge['right'])
                        y = edge['top'] + (90 - lat) / 180 * (100 - edge['top'] - edge['bottom'])
                        points.append(f"{x},{y}")
                    points_str = " ".join(points)

                    print("points", points_str)
                    
                    file_handle.write(
                        f"<polygon points='{points_str}' "
                        f"style='fill:rgba(0,255,0,0.25); stroke:green; stroke-width:0.3; cursor:pointer;' "
                        f"onclick=\"scrollToSection('{ts}')\" "
                        f"onmouseover=\"this.style.fill='rgba(0,255,0,0.4)';\" "
                        f"onmouseout=\"this.style.fill='rgba(0,255,0,0.25)';\" "
                        f"title='{ts}' />\n"
                    )

            # --- RECTANGULAR CASE ---
            elif len(lats) == 2 and len(lons) == 2:
                lat_min, lat_max = np.min(lats), np.max(lats)
                lon_min, lon_max = np.min(lons), np.max(lons)

                if lon_max - lon_min > 180:
                    boxes = [(lon_min, 180), (-180, lon_max)]
                else:
                    boxes = [(lon_min, lon_max)]

                for lon_min_box, lon_max_box in boxes:
                    left = edge['left'] + (lon_min_box + 180) / 360 * (100 - edge['left'] - edge['right'])
                    top = edge['top'] + (90 - lat_max) / 180 * (100 - edge['top'] - edge['bottom'])
                    width = (lon_max_box - lon_min_box) / 360 * (100 - edge['left'] - edge['right'])
                    height = (lat_max - lat_min) / 180 * (100 - edge['top'] - edge['bottom'])

                    
                    file_handle.write(
                        f"<rect x='{left}' y='{top}' width='{width}' height='{height}' "
                        f"style='fill:rgba(0,255,0,0.25); stroke:green; stroke-width:0.5; cursor:pointer;' "
                        f"onclick=\"scrollToSection('{ts}')\" "
                        f"onmouseover=\"this.style.fill='rgba(0,255,0,0.4)';\" "
                        f"onmouseout=\"this.style.fill='rgba(0,255,0,0.25)';\" "
                        f"title='{ts}' />\n"
                    )

        file_handle.write("</svg>\n")

    file_handle.write("</div>\n")

def generate_gallery_header(title, title2=None, logo_path=None, resolution_factor=1.0, quality=95):
    """
    Generate HTML header including title, title2 and logo for gallery pages.
    
    Parameters:
        title (str): Title text (without HTML tags)
        title2 (str): Secondary title or subtitle HTML content
        logo_path (str): Path to logo file
        resolution_factor (float): Factor to resize the image
        quality (int): JPEG quality for the image encoding
        
    Returns:
        str: HTML header content
    """
    # Check if logo_path is provided and the file exists
    include_logo = False
    logo_html = ""
    
    if logo_path and os.path.isfile(logo_path):
        # Use existing function to encode logo
        b64 = encode_image_to_base64(logo_path, factor=resolution_factor, quality=quality)
        if b64:
            include_logo = True
            # Get file extension and determine MIME type
            fname = os.path.basename(logo_path)
            ext = fname.lower().split('.')[-1]
            if ext == "png":
                mime = "png"
            elif ext == "gif":
                mime = "gif"
            elif ext == "bmp":
                mime = "bmp"
            else:
                mime = "jpeg"
            logo_src = f'data:image/{mime};base64,{b64}'
            logo_html = f'<div class="header-logo"><img src="{logo_src}" alt="Logo"></div>'
    
    # Build header HTML
    html_parts = [
        "<!DOCTYPE html>\n<html>\n<head>\n<meta charset='UTF-8'>\n",
        f"<title>{title}</title>\n",
        """
        <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        
        /* Header and logo styles */
        .header-container { position: relative; margin-bottom: 30px; padding-right: 260px; }
        .header-logo { position: absolute; top: 10px; right: 20px; z-index: 100; }
        .header-logo img { max-height: 240px; width: auto; border: none; }
        
        .gallery { display: flex; flex-direction: column; gap: 20px; }
        .row { display: flex; justify-content: center; gap: 20px; }
        .img-container { display: flex; flex-direction: column; align-items: center;
                         border: 1px solid #ccc; padding: 10px; border-radius: 10px;
                         box-shadow: 0 4px 6px rgba(0,0,0,0.1); background-color: #fafafa; }
        .img-container img { max-width: 100%; height: auto; border-radius: 5px; }
        .caption { margin-top: 10px; font-weight: bold; text-align: center; }
        .message-box { border: 1px solid #ccc; padding: 10px; border-radius: 10px;
                       background-color: #e6f7ff; margin-bottom: 20px; cursor: pointer; font-size: 14px; }
        .message-box:hover { background-color: #cceeff; }
        .long-message { display: none; margin-top: 10px; color: #555; font-size: 12px; }
        .map-container { position: relative; display: inline-block; max-width: 100%; }
        svg { position: absolute; left: 0; top: 0; width: 100%; height: 100%; }
        html { scroll-behavior: smooth; }

        .toggle-button {
            background: #0077cc;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
            margin: 15px 0;
            display: block;
        }

        @media (max-width: 768px) {
            .gallery { flex-direction: column; gap: 10px; }
            .row { flex-direction: column; }
        }

       .short-message { font-size: 18px; }
       .long-message  { font-size: 16px; }
        </style>
        """,
        """
        <script>
        function toggleMessage(id, el) {
            const content = document.getElementById(id);
            if (!content) return;
            if (content.style.display === 'none' || content.style.display === '') {
                content.style.display = 'block';
                el.classList.add('expanded');
            } else {
                content.style.display = 'none';
                el.classList.remove('expanded');
            }
        }

        function scrollToSection(id) {
            const el = document.getElementById(id);
            if (el) {
                el.scrollIntoView({ behavior: 'smooth' });
                history.pushState(null, '', '#' + id);
            }
        }

        function backToGlobal() {
            const map = document.getElementById('global-map');
            if (map) {
                map.scrollIntoView({ behavior: 'smooth' });
                history.pushState(null, '', '#global-map');
            }
        }

        window.addEventListener('scroll', function() {
            let sections = document.querySelectorAll('h2[id]');
            let scrollPos = window.scrollY || window.pageYOffset;
            for (let i = 0; i < sections.length; i++) {
                let sec = sections[i];
                if (sec.offsetTop <= scrollPos + 100) {
                    history.replaceState(null, null, '#' + sec.id);
                }
            }
        });
        </script>
        """
    ]
    
    # Create opening body tag and header content
    if include_logo:
        header_content = f"""
        </head>
        <body>
        <div class="header-container">
            <h1>{title}</h1>
            {logo_html}
        </div>
        """
    else:
        header_content = f"""
        </head>
        <body>
        <h1>{title}</h1>
        """
    
    html_parts.append(header_content)
    
    # Add title2 if provided
    if title2:
        html_parts.append(title2)
    
    return "".join(html_parts)
    
def create_html_from_subfolders(image_groups, output_html, sequence, global_map=None,
                                title="Combined Image Gallery", title2=None,
                                titlev=None, resolution_factor=1, quality=85, message1v=None, message2v=None,
                                url_base="http://oceandata.sci.gsfc.nasa.gov/getfile/",
                                sensor="PACE_HARP2", suite="L2.MAPOL_OCEAN.V3_0",
                                hide_after_key='sph', infov_dict=None, text_box=None, logo_path=None):
    """
    Create an HTML file grouping images by timestamp, with message boxes and a global map with clickable bounding boxes.
    """
    with open(output_html, "w") as f:
        # Write header with title, subtitle and logo
        f.write(generate_gallery_header(title, title2, logo_path, resolution_factor, quality))
        
        # Map
        if infov_dict:
            write_global_map_with_navigation(f, image_groups, infov_dict=infov_dict, global_map=global_map)

        # Loop through groups
        for i1, group in enumerate(image_groups):
            ts = group["timestamp"]
            images = group["images"]
            download_url = f"{url_base}{sensor}.{ts}.{suite}.nc"

            f.write(f"<h2 id='{ts}' style='text-align:center; margin-top:50px;'>")
            f.write(f"Timestamp: {ts} <a href='{download_url}' target='_blank'>L2 ⬇️</a>")
            f.write(f"<span style='margin-left:10px; cursor:pointer;' onclick='backToGlobal()' title='Back to Global Map'>🌍</span>")
            f.write("</h2><hr>\n")

            # Messages
            if message1v and message2v:
                short_msg = message2v.get(ts, "")
                long_msg = message1v.get(ts, "")
                f.write(f"<div class='message-box short-message' onclick='toggleMessage(\"long-message-{i1}\", this)'>")
                f.write("<strong> ChatGSFC AI summary 💬 </strong> (Click for more details)")
                f.write(convert_text_to_paragraphs(short_msg))
                f.write("</div>\n")
                f.write(f"<div id='long-message-{i1}' class='long-message'>")
                f.write(convert_text_to_paragraphs(long_msg))
                f.write("</div>\n")

            # Gallery
            f.write("<div class='gallery'>\n")
            write_gallery_section(images, f, sequence, titlev,
                                  resolution_factor, quality, hide_after_key, 
                                  section_id=i1, text_box=text_box)
            f.write("</div>\n")

        f.write("</body></html>\n")

    print(f"✅ Combined HTML gallery written to {output_html}")

def write_gallery_section(image_list, file_handle, sequence, titlev,
                          resolution_factor=1, quality=85, hide_after_key="sph", 
                          section_id=0, text_box=None):
    """
    Each section has its own independent 'Show More Plots' toggle.
    Images are clickable to enlarge in a modal with next/previous navigation within the same timestamp.
    Text elements create scrollable text boxes when text is too long.
    """
    valid_extensions = {".png", ".jpg", ".jpeg"}
    filtered_images = [img for img in image_list if is_valid_image(img, valid_extensions)]

    hide_started = False
    
    # Add modal HTML and JavaScript if it's the first section
    if section_id == 0:
        file_handle.write("""
        <div id="imageModal" class="modal">
            <span class="close">&times;</span>
            <img class="modal-content" id="modalImage">
            <div id="modalCaption"></div>
            <div class="prev" onclick="changeImage(-1)">&#10094;</div>
            <div class="next" onclick="changeImage(1)">&#10095;</div>
        </div>
        
        <style>
        /* Modal styles - Fixed positioning for proper centering */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
            align-items: center;
            justify-content: center;
        }
        .modal-content {
            display: block;
            max-width: 90vw;
            max-height: 90vh;
            object-fit: contain;
        }
        #modalCaption {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            color: white;
            background-color: rgba(0,0,0,0.7);
            padding: 10px 20px;
            border-radius: 5px;
            text-align: center;
            max-width: 80%;
            font-size: 16px;
        }
        .close {
            position: fixed;
            top: 20px;
            right: 30px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            transition: 0.3s;
            z-index: 1001;
            cursor: pointer;
        }
        .close:hover, .close:focus {
            color: #bbb;
            text-decoration: none;
        }
        .img-container img {
            cursor: pointer;
            transition: 0.3s;
        }
        .img-container img:hover {
            opacity: 0.8;
        }
        
        /* Text box specific styles only */
        .text-box {
            max-width: 100%;
            height: 200px;
            padding: 15px;
            box-sizing: border-box;
            background-color: #f9f9f9;
            overflow-y: auto;
            overflow-x: hidden;
            font-family: Arial, sans-serif;
            font-size: 14px;
            line-height: 1.5;
            border-radius: 5px;
            margin-bottom: 10px;
            border: 1px solid #ddd;
        }
        
        /* Custom scrollbar styling */
        .text-box::-webkit-scrollbar {
            width: 8px;
        }
        
        .text-box::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }
        
        .text-box::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 4px;
        }
        
        .text-box::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
        
        /* Navigation buttons - positioned at screen edges for easy discovery */
        .prev, .next {
            cursor: pointer;
            position: fixed;
            top: 50%;
            transform: translateY(-50%);
            width: 60px;
            height: 60px;
            color: white;
            font-weight: bold;
            font-size: 24px;
            transition: 0.3s ease;
            border-radius: 50%;
            user-select: none;
            background-color: rgba(0,0,0,0.6);
            border: 2px solid rgba(255,255,255,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1001;
        }
        .next {
            right: 20px;
        }
        .prev {
            left: 20px;
        }
        .prev:hover, .next:hover {
            background-color: rgba(0,0,0,0.9);
            border-color: rgba(255,255,255,0.8);
            transform: translateY(-50%) scale(1.1);
        }
        
        /* Hide navigation buttons when modal is closed */
        .modal:not([style*="display: flex"]) .prev,
        .modal:not([style*="display: flex"]) .next {
            display: none !important;
        }
        
        /* Toggle button styles */
        .toggle-button {
            background-color: #007cba;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            margin: 10px 0;
            transition: background-color 0.3s;
        }
        
        .toggle-button:hover {
            background-color: #005a87;
        }
        </style>
        
        <script>
        // Modal JavaScript with improved positioning and navigation
        var modal = document.getElementById('imageModal');
        var modalImg = document.getElementById('modalImage');
        var captionText = document.getElementById('modalCaption');
        var imageGalleries = {};  // Object to store images by timestamp/section
        var currentSectionId = null;
        var currentImageIndex = 0;
        
        // Function to open the modal - always centers in viewport
        function openImageModal(imgSrc, caption, sectionId, imageIndex) {
            modal.style.display = "flex"; // Use flex for perfect centering
            currentSectionId = sectionId;
            currentImageIndex = imageIndex;
            modalImg.src = imgSrc;
            captionText.innerHTML = caption;
            
            // Prevent body scroll when modal is open
            document.body.style.overflow = 'hidden';
            
            // Focus on modal for keyboard navigation
            modal.focus();
        }
        
        // Function to close modal
        function closeModal() {
            modal.style.display = "none";
            document.body.style.overflow = 'auto'; // Restore scroll
        }
        
        // Function to change image (next/previous) within the same timestamp
        function changeImage(direction) {
            if (currentSectionId === null || !imageGalleries[currentSectionId]) return;
            
            var currentGallery = imageGalleries[currentSectionId];
            currentImageIndex += direction;
            
            // Loop around if at the beginning or end of current timestamp group
            if (currentImageIndex < 0) {
                currentImageIndex = currentGallery.length - 1;
            }
            if (currentImageIndex >= currentGallery.length) {
                currentImageIndex = 0;
            }
            
            modalImg.src = currentGallery[currentImageIndex].src;
            captionText.innerHTML = currentGallery[currentImageIndex].caption;
        }
        
        // Enhanced keyboard navigation
        document.onkeydown = function(e) {
            if (modal.style.display === "flex") {
                e.preventDefault(); // Prevent default scrolling
                if (e.keyCode === 37) { // Left arrow key
                    changeImage(-1);
                }
                if (e.keyCode === 39) { // Right arrow key
                    changeImage(1);
                }
                if (e.keyCode === 27) { // Escape key
                    closeModal();
                }
            }
        }
        
        // Close button functionality
        document.getElementsByClassName('close')[0].onclick = closeModal;
        
        // Close when clicking outside the image (on modal background)
        modal.onclick = function(event) {
            if (event.target === modal) {
                closeModal();
            }
        }
        
        // Prevent clicks on image from closing modal
        modalImg.onclick = function(event) {
            event.stopPropagation();
        }
        
        // Touch support for mobile devices
        var touchStartX = null;
        
        modal.addEventListener('touchstart', function(e) {
            touchStartX = e.touches[0].clientX;
        });
        
        modal.addEventListener('touchend', function(e) {
            if (touchStartX === null) return;
            
            var touchEndX = e.changedTouches[0].clientX;
            var diff = touchStartX - touchEndX;
            
            if (Math.abs(diff) > 50) { // Minimum swipe distance
                if (diff > 0) {
                    changeImage(1); // Swipe left = next
                } else {
                    changeImage(-1); // Swipe right = previous
                }
            }
            
            touchStartX = null;
        });
        </script>
        """)

    # Initialize the gallery array for this section
    file_handle.write(f"""
    <script>
    if (!imageGalleries[{section_id}]) {{
        imageGalleries[{section_id}] = [];
    }}
    </script>
    """)

    # Build the image gallery array for navigation within this timestamp
    image_counter = 0
    for row_idx, row in enumerate(sequence):
        file_handle.write("<div class='row'>\n")
        for col_idx, col_key in enumerate(row):
            
            # Handle text elements
            if col_key == 'text_box':
                text_content = text_box if text_box else "No text content provided"
                caption = titlev[row_idx][col_idx] if titlev and len(titlev) > row_idx and len(titlev[row_idx]) > col_idx and titlev[row_idx][col_idx] else ""
                
                file_handle.write(f"""
                <div class='img-container'>
                    <div class='text-box'>
                        {text_content}
                    </div>
                    <div class='caption'>{caption}</div>
                </div>
                """)
            
            # Handle image elements
            else:
                matched_image = next((img for img in filtered_images if f"_{col_key}." in img), None)
                if matched_image:
                    encoded_image = encode_image_to_base64(matched_image, factor=resolution_factor, quality=quality)
                    caption = titlev[row_idx][col_idx] if titlev and len(titlev) > row_idx and len(titlev[row_idx]) > col_idx and titlev[row_idx][col_idx] else ""
                    image_id = f"img_{section_id}_{row_idx}_{col_idx}"
                    
                    # Make the image clickable - now passes section_id and image_counter within section
                    file_handle.write(f"""
                    <div class='img-container'>
                        <img id="{image_id}" src='data:image/jpeg;base64,{encoded_image}' 
                             alt='{caption}' onclick="openImageModal(this.src, '{caption}', {section_id}, {image_counter})">
                        <div class='caption'>{caption}</div>
                    </div>
                    """)
                    
                    # Add image to JavaScript gallery array for this specific section
                    file_handle.write(f"""
                    <script>
                    imageGalleries[{section_id}].push({{
                        src: 'data:image/jpeg;base64,{encoded_image}',
                        caption: '{caption}'
                    }});
                    </script>
                    """)
                    
                    image_counter += 1
                
        file_handle.write("</div>\n")

        # Start hiding after target key
        if hide_after_key and any(hide_after_key in key for key in row) and not hide_started:
            hide_started = True

            hidden_id = f"hidden-plots-{section_id}"
            btn_id = f"toggle-btn-{section_id}"

            # unique toggle button and JS function
            file_handle.write(f"""
            <button id="{btn_id}" class="toggle-button" onclick="toggleHiddenPlots_{section_id}()">Show More Plots</button>
            <div id="{hidden_id}" style="display:none;">

            <script>
            function toggleHiddenPlots_{section_id}() {{
                const section = document.getElementById('{hidden_id}');
                const btn = document.getElementById('{btn_id}');
                if (section.style.display === 'none') {{
                    section.style.display = 'block';
                    btn.textContent = 'Hide Plots';
                }} else {{
                    section.style.display = 'none';
                    btn.textContent = 'Show More Plots';
                }}
            }}
            </script>
            """)

    if hide_started:
        file_handle.write("</div>\n")


