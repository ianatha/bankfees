#!/usr/bin/env python3
"""
PDF Footer Tool

Adds a footer with retrieval date and URL to each page of a PDF.
"""

import argparse
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def add_footer(input_path, output_path, footer_lines):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page_num, page in enumerate(reader.pages):
        # Create a PDF in memory with footer
        packet = BytesIO()
        # Use page media size
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        # Register custom font (DejaVuSans) if not already registered
        font_path = "/Library/Fonts/DejaVuSans.ttf"
        if not os.path.exists(font_path):
            # Fallback to a bundled font or another path if needed
            font_path = "/System/Library/Fonts/Supplemental/Courier New Bold.ttf"
        pdfmetrics.registerFont(TTFont("CourierNewBold", font_path))
        can = canvas.Canvas(packet, pagesize=(width, height))
        can.setFont("CourierNewBold", 8)
        # Start drawing from 0.65 inch, with 0.15 inch line spacing
        y = 0.65 * inch
        for line in footer_lines:
            can.drawString(0.5 * inch, y, line)
            y -= 0.15 * inch
        can.save()
        packet.seek(0)
        overlay_pdf = PdfReader(packet)
        overlay_page = overlay_pdf.pages[0]
        # Merge overlay onto original page
        page.merge_page(overlay_page)
        writer.add_page(page)
    # Write out the updated PDF
    with open(output_path, "wb") as out_f:
        writer.write(out_f)

def main():
    parser = argparse.ArgumentParser(description="Add footer to PDF pages.")
    parser.add_argument("input_pdf", help="Path to input PDF file.")
    parser.add_argument("output_pdf", help="Path to output PDF file.")
    parser.add_argument("--date", required=True, help="Retrieval date (e.g., 2025-06-11).")
    parser.add_argument("--url", required=True, help="URL from which PDF was retrieved.")
    args = parser.parse_args()
    add_footer(args.input_pdf, args.output_pdf, [
        "*** Ε.Κ.ΠΟΙ.ΖΩ.",
        f"*** Ανακτήθηκε στις {args.date} από {args.url}"
    ]
)

if __name__ == "__main__":
    main()
