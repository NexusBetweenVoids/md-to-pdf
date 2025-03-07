"""
Tests for the Markdown to PDF converter

This module contains basic tests for the converter functionality.
"""

import os
import unittest
from converter import convert_md_to_pdf

class TestConverter(unittest.TestCase):
    """Test cases for the converter module."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_path = os.path.join(self.test_dir, 'test_output.pdf')
    
    def tearDown(self):
        """Clean up after tests."""
        if os.path.exists(self.output_path):
            os.remove(self.output_path)
    
    def test_basic_conversion(self):
        """Test basic Markdown to PDF conversion."""
        markdown_content = "# Test Heading\n\nThis is a test paragraph."
        result = convert_md_to_pdf(markdown_content, self.output_path)
        # Check that the file was created
        self.assertTrue(os.path.exists(self.output_path))
        # Check that the file has content
        self.assertGreater(os.path.getsize(self.output_path), 0)
    
    def test_with_links(self):
        """Test conversion with links."""
        markdown_content = "# Test Links\n\n[Example Link](https://example.com)"
        result = convert_md_to_pdf(markdown_content, self.output_path)
        self.assertTrue(os.path.exists(self.output_path))
    
    def test_with_toc(self):
        """Test conversion with table of contents."""
        markdown_content = """# Main Heading
## Section 1
Content for section 1
## Section 2
Content for section 2
### Subsection 2.1
Content for subsection 2.1
"""
        result = convert_md_to_pdf(markdown_content, self.output_path, include_toc=True)
        self.assertTrue(os.path.exists(self.output_path))

if __name__ == '__main__':
    unittest.main()