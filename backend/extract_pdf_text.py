#!/usr/bin/env python3
"""
Extract text from a PDF and save to a UTF-8 .txt file.
Usage:
  python extract_pdf_text.py --input "c:/MAIN-PROJECT/health-data-exchange/Privacy_Preserving_Data_Imputation_via_Multi-Party_Computation_for_Medical_Applications-c.pdf" --output backend/_tmp_pdf_text.txt

Requires: PyPDF2
  pip install PyPDF2
"""
import argparse
import sys

try:
    from PyPDF2 import PdfReader
except ImportError:
    print("PyPDF2 is not installed. Install it with: pip install PyPDF2", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Extract text from PDF")
    parser.add_argument("--input", required=True, help="Path to PDF file")
    parser.add_argument("--output", required=True, help="Path to output .txt file")
    args = parser.parse_args()

    reader = PdfReader(args.input)
    texts = []
    for i, page in enumerate(reader.pages):
        try:
            texts.append(page.extract_text() or "")
        except Exception as e:
            texts.append(f"\n[Error extracting page {i}: {e}]\n")
    content = "\n\n".join(texts)

    with open(args.output, "w", encoding="utf-8", errors="ignore") as f:
        f.write(content)
    print(f"Wrote text to: {args.output}")


if __name__ == "__main__":
    main()
