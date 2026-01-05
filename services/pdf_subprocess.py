#!/usr/bin/env python3
"""
Subprocess script for PDF generation.

This script runs WeasyPrint in an isolated subprocess where DYLD_FALLBACK_LIBRARY_PATH
is properly set, bypassing macOS SIP restrictions that strip DYLD_* variables
from parent-to-child process inheritance in certain contexts (like uvicorn).

Usage: python pdf_subprocess.py <html_path> <css_path> <output_path>
"""
import sys
from pathlib import Path


def generate_pdf(html_path: str, css_path: str, output_path: str) -> None:
    """Generate PDF from HTML file using WeasyPrint."""
    from weasyprint import HTML, CSS

    html_doc = HTML(filename=html_path)
    css = CSS(filename=css_path)
    html_doc.write_pdf(output_path, stylesheets=[css])


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python pdf_subprocess.py <html_path> <css_path> <output_path>", file=sys.stderr)
        sys.exit(1)

    html_path, css_path, output_path = sys.argv[1:4]

    # Validate paths exist
    if not Path(html_path).exists():
        print(f"HTML file not found: {html_path}", file=sys.stderr)
        sys.exit(1)
    if not Path(css_path).exists():
        print(f"CSS file not found: {css_path}", file=sys.stderr)
        sys.exit(1)

    generate_pdf(html_path, css_path, output_path)
