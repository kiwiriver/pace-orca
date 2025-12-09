#!/usr/bin/env python3
"""
HTML Viewer Generator for PACE Data
Generates an HTML viewer for browsing HTML files in a specified directory.
Supports different filename parsing modes for dates/timestamps.
"""

import os
import argparse
import re
from pathlib import Path

def generate_html_viewer(base_url, title="PACE Data Viewer", output="index.html", parse_mode="auto"):
    """
    Generate HTML viewer with specified base URL, title, and parsing mode.
    
    Args:
        base_url (str): Base URL or path for the data files
        title (str): Title for the HTML page
        output (str): Output HTML filename
        parse_mode (str): How to parse filenames - "date", "timestamp", or "auto"

        base_url: https://oceancolor.gsfc.nasa.gov/fileshare/meng_gao/rapid_pace/html/
        

        python orca_html_index.py --base-url "https://oceancolor.gsfc.nasa.gov/fileshare/meng_gao/rapid_pace/html/" --title "PACE Data Viewer" output="index.html" --parse-mode date

        python orca_html_index.py --base-url "https://oceancolor.gsfc.nasa.gov/fileshare/meng_gao/pace/spotlight/html/" --title "PACE Data Viewer" output="index.html" --parse-mode timestamp
    """
    
    # Generate JavaScript functions based on parse mode
    if parse_mode == "date":
        extract_function = '''
function extractDate(filename) {
  // Extract date from format like 2025-11-09
  const m = filename.match(/(\\d{4}-\\d{2}-\\d{2})/);
  return m ? m[1] : null;
}

function formatDisplayValue(value) {
  return value; // Already in readable format
}

function createSimplifiedLabel(filename, index) {
  let instrument = '';
  let algorithm = '';
  
  if (filename.includes('harp2_fastmapol')) {
    instrument = 'HARP2';
    algorithm = 'FastMAPOL';
  } else if (filename.includes('spexone_fastmapol')) {
    instrument = 'SPEXone';
    algorithm = 'FastMAPOL';
  } else if (filename.includes('spexone_remotap')) {
    instrument = 'SPEXone';
    algorithm = 'REMOTAP';
  }
  
  const date = extractDate(filename);
  return `${instrument} ${algorithm} - ${date} (${index})`;
}'''
        input_label = "Date (YYYY-MM-DD)"
        input_placeholder = "auto detect"
        list_id = "dateList"
        input_id = "dateInput"
        
    elif parse_mode == "timestamp":
        extract_function = '''
function extractDate(filename) {
  // Extract timestamp from format like 20240906T202704
  const m = filename.match(/(\\d{8}T\\d{6})/);
  return m ? m[1] : null;
}

function formatDisplayValue(timestamp) {
  // Convert 20240906T202704 to "2024-09-06 20:27:04"
  if (!timestamp || timestamp.length !== 15) return timestamp;
  
  const year = timestamp.substr(0, 4);
  const month = timestamp.substr(4, 2);
  const day = timestamp.substr(6, 2);
  const hour = timestamp.substr(9, 2);
  const minute = timestamp.substr(11, 2);
  const second = timestamp.substr(13, 2);
  
  return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
}

function createSimplifiedLabel(filename, index) {
  let instrument = '';
  let algorithm = '';
  
  if (filename.includes('harp2_fastmapol')) {
    instrument = 'HARP2';
    algorithm = 'FastMAPOL';
  } else if (filename.includes('spexone_fastmapol')) {
    instrument = 'SPEXone';
    algorithm = 'FastMAPOL';
  } else if (filename.includes('spexone_remotap')) {
    instrument = 'SPEXone';
    algorithm = 'REMOTAP';
  }
  
  const timestamp = extractDate(filename);
  const formattedTime = formatDisplayValue(timestamp);
  
  return `${instrument} ${algorithm} - ${formattedTime} (${index})`;
}'''
        input_label = "Timestamp (YYYYMMDDTHHMMSS)"
        input_placeholder = "auto detect"
        list_id = "timestampList"
        input_id = "timestampInput"
        
    else:  # auto mode
        extract_function = '''
function extractDate(filename) {
  // Try timestamp format first (20240906T202704)
  let m = filename.match(/(\\d{8}T\\d{6})/);
  if (m) return m[1];
  
  // Try date format (2025-11-09)
  m = filename.match(/(\\d{4}-\\d{2}-\\d{2})/);
  return m ? m[1] : null;
}

function formatDisplayValue(value) {
  if (!value) return value;
  
  // If it's a timestamp format (20240906T202704)
  if (value.length === 15 && value.includes('T')) {
    const year = value.substr(0, 4);
    const month = value.substr(4, 2);
    const day = value.substr(6, 2);
    const hour = value.substr(9, 2);
    const minute = value.substr(11, 2);
    const second = value.substr(13, 2);
    return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
  }
  
  // Otherwise return as-is (already formatted date)
  return value;
}

function createSimplifiedLabel(filename, index) {
  let instrument = '';
  let algorithm = '';
  
  if (filename.includes('harp2_fastmapol')) {
    instrument = 'HARP2';
    algorithm = 'FastMAPOL';
  } else if (filename.includes('spexone_fastmapol')) {
    instrument = 'SPEXone';
    algorithm = 'FastMAPOL';
  } else if (filename.includes('spexone_remotap')) {
    instrument = 'SPEXone';
    algorithm = 'REMOTAP';
  }
  
  const dateTime = extractDate(filename);
  const formattedTime = formatDisplayValue(dateTime);
  
  return `${instrument} ${algorithm} - ${formattedTime} (${index})`;
}'''
        input_label = "Date/Timestamp"
        input_placeholder = "auto detect"
        list_id = "dateList"
        input_id = "dateInput"

    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  body {{
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    height: 100vh;
  }}
  header {{
    background: #f0f0f0;
    padding: 10px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }}
  .top-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}
  input {{
    padding: 5px;
    font-size: 1rem;
    width: 150px;
  }}
  #{list_id} {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 5px;
  }}
  #{list_id} button {{
    background: #e6e6e6;
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 4px 8px;
    cursor: pointer;
    font-size: 0.9rem;
  }}
  #{list_id} button:hover {{
    background: #d0d0d0;
  }}
  #columnToggles {{
    display: flex;
    gap: 6px;
    margin-top: 6px;
  }}
  #columnToggles button {{
    background: #0077cc;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 5px 10px;
    cursor: pointer;
  }}
  #columnToggles button.active {{
    background: #004c99;
  }}
  main {{
    flex: 1;
    display: flex;
    overflow: hidden;
    transition: all 0.3s ease;
  }}
  .column {{
    flex: 1;
    overflow-y: auto;
    padding: 10px;
    border-right: 1px solid #ddd;
    transition: flex 0.3s ease;
  }}
  .column:last-child {{
    border-right: none;
  }}
  .column h2 {{
    text-align: center;
    background: #fafafa;
    margin: 0;
    padding: 15px 0;
    color: #0066cc;
    cursor: pointer;
    text-decoration: underline;
  }}
  a {{
    text-decoration: none;
    color: #0066cc;
    display: block;
    margin: 5px 0;
    word-wrap: break-word;
  }}
  iframe {{
    width: 100%;
    height: 8000px;
    border: none;
    border-radius: 5px;
    margin-bottom: 10px;
  }}
  .file-label {{
    font-weight: bold;
    color: #333;
    margin: 10px 0 5px 0;
    padding: 5px;
    background: #f9f9f9;
    border-left: 3px solid #0066cc;
  }}
</style>
</head>
<body>
  <header>
    <div class="top-row">
      <h3>{title}</h3>
      <div>
        <label for="{input_id}">{input_label}: </label>
        <input id="{input_id}" placeholder="{input_placeholder}" />
        <button onclick="updateView()">Go</button>
      </div>
    </div>

    <div id="{list_id}"></div>
    <div id="columnToggles">
      <button class="active" data-col="col1">HARP2 FastMAPOL</button>
      <button class="active" data-col="col2">SPEXone FastMAPOL</button>
      <button class="active" data-col="col3">SPEXone REMOTAP</button>
    </div>
  </header>

  <main>
    <div class="column" id="col1">
      <h2>HARP2 FastMAPOL</h2>
    </div>
    <div class="column" id="col2">
      <h2>SPEXone FastMAPOL</h2>
    </div>
    <div class="column" id="col3">
      <h2>SPEXone REMOTAP</h2>
    </div>
  </main>

<script>
const baseURL = "{base_url}";

const keywords = {{
  col1: "harp2_fastmapol",
  col2: "spexone_fastmapol",
  col3: "spexone_remotap"
}};

// Fetch file list
async function fetchFileList() {{
  const response = await fetch(baseURL);
  const text = await response.text();
  const matches = [...text.matchAll(/href="([^"]+\\.html)"/g)];
  return matches.map(m => m[1]);
}}

{extract_function}

async function updateView(targetValue = null) {{
  const files = await fetchFileList();
  const inputValue = document.getElementById("{input_id}").value.trim();
  const values = [...new Set(files.map(extractDate).filter(Boolean))].sort();
  const listContainer = document.getElementById("{list_id}");

  // --- Populate buttons ---
  listContainer.innerHTML = "";
  values.forEach(v => {{
    const btn = document.createElement("button");
    btn.textContent = formatDisplayValue(v);
    btn.onclick = () => {{
      document.getElementById("{input_id}").value = v;
      updateView(v);
    }};
    listContainer.appendChild(btn);
  }});

  const selectedValue = targetValue || inputValue || values[values.length - 1];

  // Reset columns
  for (const [id, key] of Object.entries(keywords)) {{
    document.getElementById(id).innerHTML = `<h2>${{key.replace(/_/g, ' ').toUpperCase()}}</h2>`;
  }}

  // Filter files by selected value
  const selectedFiles = files.filter(f => extractDate(f) === selectedValue);

  // Group files by column and add sequential numbering
  for (const [colId, key] of Object.entries(keywords)) {{
    const col = document.getElementById(colId);
    const matchingFiles = selectedFiles.filter(f => f.includes(key));
    
    matchingFiles.forEach((f, index) => {{
      const block = document.createElement("div");
      const simplifiedLabel = createSimplifiedLabel(f, index + 1);
      
      block.innerHTML = `
        <div class="file-label">${{simplifiedLabel}}</div>
        <a href="${{baseURL + f}}" target="_blank">${{f}}</a>
        <iframe src="${{baseURL + f}}"></iframe>
      `;
      col.appendChild(block);
    }});
  }}

  document.title = `{title} - ${{formatDisplayValue(selectedValue)}}`;
}}

// --- Toggle column visibility ---
document.addEventListener("DOMContentLoaded", () => {{
  const toggleButtons = document.querySelectorAll("#columnToggles button");
  toggleButtons.forEach(btn => {{
    btn.addEventListener("click", () => {{
      const colId = btn.dataset.col;
      const col = document.getElementById(colId);
      const isActive = btn.classList.toggle("active");

      if (isActive) {{
        col.style.display = "block";
      }} else {{
        col.style.display = "none";
      }}

      // Recalculate visible columns and adjust width
      const visibleCols = [...document.querySelectorAll(".column")]
        .filter(c => c.style.display !== "none");
      const widthPercent = 100 / visibleCols.length;
      visibleCols.forEach(c => (c.style.flex = `0 0 ${{widthPercent}}%`));
    }});
  }});

  updateView();
}});
</script>
</body>
</html>'''

    # Write the HTML file
    with open(output, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"HTML viewer generated: {output}")
    print(f"Base URL: {base_url}")
    print(f"Title: {title}")
    print(f"Parse mode: {parse_mode}")

def main():
    parser = argparse.ArgumentParser(
        description="Generate HTML viewer for PACE data files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Parse Modes:
  date      - Extract dates in YYYY-MM-DD format (e.g., spexone_fastmapol_2025-11-09_...)
  timestamp - Extract timestamps in YYYYMMDDTHHMMSS format (e.g., harp2_fastmapol_20240906T202704_...)
  auto      - Automatically detect both formats (default)

Examples:
  # Auto-detect filename format
  python generate_viewer.py --base-url "https://example.com/data/" --title "PACE Viewer"
  
  # Force date parsing mode
  python generate_viewer.py --base-url "https://example.com/data/" --title "PACE Viewer" --parse-mode date
  
  # Force timestamp parsing mode
  python generate_viewer.py --base-url "https://example.com/data/" --title "PACE Viewer" --parse-mode timestamp
        """
    )
    
    parser.add_argument(
        '--base-url',
        required=True,
        help='Base URL or path for the data files (should end with /)'
    )
    
    parser.add_argument(
        '--title',
        default='Data Viewer',
        help='Title for the HTML page (default: "Data Viewer")'
    )
    
    parser.add_argument(
        '--output',
        default='viewer.html',
        help='Output HTML filename (default: "viewer.html")'
    )
    
    parser.add_argument(
        '--parse-mode',
        choices=['date', 'timestamp', 'auto'],
        default='auto',
        help='How to parse filenames: date (YYYY-MM-DD), timestamp (YYYYMMDDTHHMMSS), or auto-detect (default: auto)'
    )
    
    args = parser.parse_args()
    
    # Ensure base URL ends with /
    base_url = args.base_url
    if not base_url.endswith('/'):
        base_url += '/'
    
    # Generate the HTML viewer
    generate_html_viewer(
        base_url=base_url,
        title=args.title,
        output=args.output,
        parse_mode=args.parse_mode
    )

if __name__ == "__main__":
    main()