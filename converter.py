import markdown
import os
import re
from weasyprint import HTML

def generate_toc(html_content):
    """
    Generate a table of contents from HTML content
    
    Args:
        html_content (str): HTML content
        
    Returns:
        tuple: (toc_html, modified_html_content) or empty string if no headings
    """
    # Extract all headings with their IDs
    headings = []
    
    # Find all h1, h2, h3, h4, h5, h6 tags
    pattern = r'<h([1-6])>(.*?)</h\1>'
    matches = re.findall(pattern, html_content)
    
    if not matches:
        return ""  # No headings found
    
    # If there's only one heading, we might not need a TOC
    if len(matches) < 2:
        # Still add the ID to the single heading for future reference
        level, title = matches[0]
        heading_id = title.lower().replace(' ', '-')
        heading_id = re.sub(r'[^a-z0-9-]', '', heading_id)
        
        html_content = html_content.replace(
            f'<h{level}>{title}</h{level}>',
            f'<h{level} id="{heading_id}">{title}</h{level}>'
        )
        return "", html_content
    
    # Process all headings and add IDs
    for level, title in matches:
        # Create an ID from the title
        heading_id = title.lower().replace(' ', '-')
        # Clean up any non-alphanumeric characters
        heading_id = re.sub(r'[^a-z0-9-]', '', heading_id)
        
        # Make sure the ID is unique by adding a number if needed
        base_id = heading_id
        count = 0
        while any(h['id'] == heading_id for h in headings):
            count += 1
            heading_id = f"{base_id}-{count}"
        
        headings.append({
            'level': int(level),
            'title': title,
            'id': heading_id
        })
        
        # Replace the heading in the original HTML with one that has an ID
        html_content = html_content.replace(
            f'<h{level}>{title}</h{level}>',
            f'<h{level} id="{heading_id}">{title}</h{level}>'
        )
    
    # Generate TOC HTML with proper nesting
    toc_html = '<div class="toc"><h2>Table of Contents</h2>'
    
    # Normalize heading levels for better hierarchy
    # Find the minimum heading level used
    min_level = min(heading['level'] for heading in headings)
    
    # Track current level for proper nesting
    current_level = 0
    
    # Create the nested TOC structure
    for heading in headings:
        # Adjust level relative to the minimum level found
        adjusted_level = heading['level'] - min_level + 1
        level = adjusted_level
        
        # Start new lists or close existing ones based on level changes
        if level > current_level:
            # Open new nested lists
            for _ in range(level - current_level):
                if current_level > 0:  # Don't add ul before the first item
                    toc_html += '<ul>'
                else:
                    toc_html += '<ul class="toc-level-1">'
        elif level < current_level:
            # Close higher level lists
            for _ in range(current_level - level):
                toc_html += '</ul>'
        
        # Add the list item for this heading
        toc_html += f'<li class="toc-level-{level}"><a href="#{heading["id"]}">{heading["title"]}</a></li>'
        
        # Update current level
        current_level = level
    
    # Close any remaining open lists
    for _ in range(current_level):
        toc_html += '</ul>'
    
    toc_html += '</div>'
    
    return toc_html, html_content

def convert_md_to_pdf(md_content, output_path=None, include_toc=True):
    """
    Convert markdown content to PDF
    
    Args:
        md_content (str): Markdown content
        output_path (str, optional): Output file path
        include_toc (bool): Whether to include a table of contents
        
    Returns:
        bytes or None: PDF content as bytes if output_path is None, otherwise None
    """
    # Use a simpler approach with core extensions for better link compatibility
    extensions = [
        'tables',
        'fenced_code',
        'extra',            # Includes many useful extensions
    ]
    
    # Convert markdown to HTML using Python Markdown
    html_content = markdown.markdown(md_content, extensions=extensions)
    
    # Process HTML to manually make links clickable in the PDF output
    try:
        from bs4 import BeautifulSoup
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # First, let's handle all the existing links 
        for link in soup.find_all('a'):
            if link.has_attr('href'):
                href = link['href']
                
                # Fix URLs without http/https
                if not href.startswith(('#', '/', 'mailto:')) and not href.startswith(('http://', 'https://')):
                    href = 'https://' + href
                    link['href'] = href
                
                # Replace the link with a more explicit structure proven to work in PDF
                new_link = soup.new_tag('a')
                new_link['href'] = href
                new_link['style'] = "color: blue; text-decoration: underline; cursor: pointer;"
                
                # Preserve the text content
                new_link.string = link.get_text()
                link.replace_with(new_link)
        
        # Also, let's find URLs in text that are not already links
        for text in soup.find_all(string=True):
            if text.parent.name != 'a' and text.parent.name != 'code' and text.parent.name != 'pre':
                # Simple URL pattern
                import re
                url_pattern = r'(https?://[^\s<>"\']+)'
                
                # Check if there's a URL in this text
                if re.search(url_pattern, text):
                    new_html = text
                    # Replace URLs with <a> tags
                    new_html = re.sub(
                        url_pattern,
                        r'<a href="\1" style="color: blue; text-decoration: underline; cursor: pointer;">\1</a>',
                        str(text)
                    )
                    # Only replace if changes were made
                    if new_html != text:
                        new_soup = BeautifulSoup(new_html, 'html.parser')
                        text.replace_with(new_soup)
        
        # Update the HTML content
        html_content = str(soup)
    except Exception as e:
        # If there's any error, continue with the original HTML
        print(f"Warning: Could not process links in HTML: {e}")
        pass
    
    # Generate TOC if requested
    toc_html = ""
    if include_toc:
        toc_result = generate_toc(html_content)
        if toc_result:  # Check if toc_result is not an empty string
            toc_html, html_content = toc_result
    
    # Wrap HTML with optimized styling for PDF links
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="generator" content="md-to-pdf">
        <meta name="pdf:hyperlinks" content="true">
        <meta name="pdfkit:enable-smart-shrinking" content="true">
        <meta name="pdfkit:enable-javascript" content="true">
        <script>
            // This JavaScript won't execute but helps signal to rendering engines
            // that links should be interactive
            document.addEventListener('DOMContentLoaded', function() {{
                var links = document.getElementsByTagName('a');
                for(var i = 0; i < links.length; i++) {{
                    links[i].addEventListener('click', function(e) {{
                        window.location.href = this.getAttribute('href');
                    }});
                }}
            }});
        </script>
        <style>
            body {{ 
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 2cm;
            }}
            code {{
                background-color: #f5f5f5;
                padding: 2px 4px;
                border-radius: 4px;
                font-family: monospace;
            }}
            pre {{
                background-color: #f5f5f5;
                padding: 10px;
                border-radius: 4px;
                overflow-x: auto;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            h1, h2, h3, h4, h5, h6 {{
                color: #333;
                margin-top: 20px;
            }}
            /* Enhanced link styles for better PDF compatibility */
            a {{
                color: #0066cc;
                text-decoration: underline;
            }}
            
            /* PDF-specific link styling */
            .pdf-link {{
                color: #0066cc;
                text-decoration: underline;
                border-bottom: none;
            }}
            
            /* Make external links visually distinct */
            .external-link {{
                color: #0066cc;
                font-weight: 500;
                text-decoration: underline;
            }}
            
            /* Special handling for TOC links */
            .toc a {{
                color: #444;
                display: block;
                text-decoration: none;
                border-bottom: none;
            }}
            
            .toc a:hover {{
                color: #0066cc;
                text-decoration: underline;
            }}
            /* Don't show URL for TOC links */
            .toc a::after {{
                content: "";
            }}
            /* Don't show URL for image links */
            a[href$=".jpg"]::after, 
            a[href$=".jpeg"]::after, 
            a[href$=".png"]::after, 
            a[href$=".gif"]::after, 
            a[href$=".svg"]::after,
            a[href$=".webp"]::after {{
                content: "";
            }}
            /* Table of Contents Styles */
            .toc {{
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px 25px;
                margin: 20px 0 30px 0;
                page-break-after: always;
            }}
            .toc h2 {{
                margin-top: 0;
                margin-bottom: 15px;
                padding-bottom: 5px;
                border-bottom: 1px solid #ddd;
                color: #333;
            }}
            .toc ul {{
                list-style-type: none;
                padding-left: 0;
                margin: 0;
            }}
            .toc ul ul {{
                padding-left: 20px;
            }}
            .toc li {{
                margin: 5px 0;
                padding: 2px 0;
            }}
            .toc a {{
                text-decoration: none;
                color: #333;
                display: inline-block;
                width: 100%;
            }}
            .toc a:hover {{
                color: #007bff;
            }}
            .toc-level-1 {{
                margin-bottom: 8px;
            }}
            .toc-level-1 > li > a {{
                font-weight: bold;
                font-size: 1.05em;
            }}
            .toc-level-2 > li > a {{
                padding-left: 10px;
            }}
            .toc-level-3 > li > a {{
                padding-left: 20px;
                font-size: 0.95em;
            }}
            .toc-level-4 > li > a,
            .toc-level-5 > li > a,
            .toc-level-6 > li > a {{
                padding-left: 30px;
                font-size: 0.9em;
                color: #555;
            }}
            @page {{
                @top-right {{
                    content: "Page " counter(page);
                }}
            }}
        </style>
    </head>
    <body>
        {toc_html}
        {html_content}
    </body>
    </html>
    """
    
    # Try a more direct approach with WeasyPrint
    try:
        # First try the simpler approach that's known to work with basic links
        pdf = HTML(string=styled_html).write_pdf()
    except Exception:
        # If that fails, try a more explicit approach
        try:
            from weasyprint import HTML, CSS
            
            # Create basic CSS for links
            link_css = CSS(string="""
                a { color: blue; text-decoration: underline; }
            """)
            
            # Create HTML with base URL for better link handling
            html = HTML(string=styled_html, base_url=".")
            
            # Render with explicit CSS
            pdf = html.write_pdf(stylesheets=[link_css])
        except Exception as e:
            # If all else fails, use the most basic approach
            print(f"Warning: Using fallback PDF rendering due to: {e}")
            pdf = HTML(string=styled_html).write_pdf()
    
    # Save to file if output path is provided
    if output_path:
        with open(output_path, 'wb') as f:
            f.write(pdf)
        return None
    
    # Return PDF content as bytes
    return pdf

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python converter.py <input_md_file> <output_pdf_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    convert_md_to_pdf(md_content, output_file)
    print(f"Converted '{input_file}' to '{output_file}'")