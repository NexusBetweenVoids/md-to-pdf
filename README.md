# Markdown to PDF Converter

A web application that converts Markdown files to PDF documents with advanced formatting and features. Build using Claude Code. 

[![License: GPLv3](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://opensource.org/license/gpl-3-0)

## Features

- **Upload or Paste**: Upload Markdown files (.md, .markdown) or enter Markdown text directly
- **Table of Contents**: Automatic generation of clickable table of contents
- **Links**: Fully functional clickable links in the PDF output
- **Styling**: Professional styling for headings, code blocks, tables, and more
- **Page Numbers**: Automatic page numbering for better document navigation
- **Instant Download**: Generate and download the PDF immediately
- **Responsive Interface**: Mobile-friendly web UI
- **File Size**: Support for documents up to 10MB

## Screenshots

<!-- Add screenshots of your application here -->
![Screenshot of the App](https://raw.githubusercontent.com/NexusBetweenVoids/md-to-pdf/refs/heads/main/screenshot.png)

## Installation

### Prerequisites

- Python 3.6+
- pip (Python package manager)
- System dependencies for WeasyPrint (see note below)

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/md-to-pdf.git
   cd md-to-pdf
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   > **Note**: WeasyPrint has system dependencies that vary by operating system. Please check [WeasyPrint's installation documentation](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation) for details specific to your platform.

## Usage

### Web Interface

1. Start the web server:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000/
   ```

3. Either upload a Markdown file or enter Markdown text directly, choose whether to include a table of contents, then click "Convert to PDF".

### Environment Variables

You can configure the application using the following environment variables:

- `HOST`: The host to bind the server to (default: `0.0.0.0`)
- `PORT`: The port to run the server on (default: `5000`)
- `DEBUG`: Enable debug mode (`true` or `false`, default: `false`)
- `SECRET_KEY`: Flask secret key for session security (auto-generated if not provided)

### Command Line Usage

You can also use the converter directly from the command line:

```bash
python converter.py input.md output.pdf
```

For advanced options:

```bash
python -c "import converter; converter.convert_md_to_pdf(open('input.md').read(), 'output.pdf', include_toc=True)"
```

## Deployment

### Docker

To run the application in Docker:

```bash
# Build the image
docker build -t md-to-pdf .

# Run the container
docker run -p 5000:5000 md-to-pdf
```

### Production Deployment

For production deployment, consider using a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Or with a reverse proxy like Nginx for better performance and security.

## Project Structure

- `app.py`: Flask web application with routing and request handling
- `converter.py`: Core conversion functionality (Markdown to HTML to PDF)
- `templates/index.html`: Web interface template
- `uploads/`: Directory for storing temporary files (PDFs)
- `requirements.txt`: Python dependencies
- `LICENSE`: GPLv3 License file
- `.gitignore`: Git ignore file

## Dependencies

- **Flask**: Web framework
- **Markdown**: Markdown to HTML conversion
- **WeasyPrint**: HTML to PDF conversion
- **Beautiful Soup**: HTML parsing and modification
- **PyMdown Extensions**: Extended Markdown features

## Development

To contribute to this project:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [WeasyPrint](https://weasyprint.org/) for the PDF generation capability
- [Python Markdown](https://python-markdown.github.io/) for Markdown parsing
- All open-source contributors
