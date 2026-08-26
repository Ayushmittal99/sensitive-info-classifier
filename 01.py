"""
redact_pdf.py — Replace sensitive information in ANY PDF with 'X'.

Detects common PII via regex (emails, phone numbers, SSNs, credit card
numbers, IP addresses) and permanently redacts each match: the
underlying text is removed (not just visually covered) and replaced
with a black box containing X's, so the original data can't be
recovered by copy-pasting or re-extracting text.

Just run the script — it will ask you for the path to any PDF:

    python redact_pdf.py

You can also still pass the path directly:

    python redact_pdf.py input.pdf
    python redact_pdf.py input.pdf output.pdf
    python redact_pdf.py input.pdf output.pdf "John Doe" "Acme Corp"
"""

import os
import re
import sys

import fitz  # PyMuPDF

# ---------------------------------------------------------------------
# Regex patterns for common sensitive info. Add/remove as needed.
# ---------------------------------------------------------------------
PATTERNS = {
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    # Indian mobile numbers: +91 98765 43210, 98765-43210, 9876543210, etc.
    "phone_in": r"(?:\+?91[-.\s]?)?\b[6-9]\d{4}[-.\s]?\d{5}\b",
    # General international / US-style phone numbers
    "phone_intl": r"(\+?\d{1,3}[-.\s]?)?\(?\d{3,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    # Credit/debit card numbers: 13-19 digits, optionally grouped in 4s
    "credit_card": r"\b(?:\d{4}[ -]?){3}\d{1,7}\b",
    "aadhaar": r"\b\d{4}\s?\d{4}\s?\d{4}\b",  # 12-digit Indian ID, often spaced
    "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "ifsc_code": r"\b[A-Z]{4}0[A-Z0-9]{6}\b",              # Indian bank IFSC code
    "customer_id": r"\b(?:CUST|CUSTOMER|ACC|ACCT)[-_]?\d{4,}\b",  # customer/account IDs
    "cvv_labeled": r"(?<=CVV:\s)\d{3,4}\b",                # CVV value after 'CVV:' label
    "card_expiry": r"\b(?:0[1-9]|1[0-2])/\d{2,4}\b",       # MM/YY or MM/YYYY expiry dates
    "pan_card": r"\b[A-Z]{5}\d{4}[A-Z]\b",                 # Indian PAN card number
}

# Add any extra literal terms you always want redacted (names, IDs, etc.)
CUSTOM_TERMS = []


def find_matches(text, extra_terms):
    """Return a set of exact strings in `text` that should be redacted."""
    matches = set()
    for pattern in PATTERNS.values():
        for m in re.finditer(pattern, text):
            matches.add(m.group())
    for term in extra_terms:
        if term and term in text:
            matches.add(term)
    return matches


def redact_pdf(input_path, output_path, extra_terms=None):
    extra_terms = extra_terms or CUSTOM_TERMS
    doc = fitz.open(input_path)
    total_redactions = 0

    for page in doc:
        text = page.get_text()
        matches = find_matches(text, extra_terms)

        for match in matches:
            areas = page.search_for(match)
            for rect in areas:
                replacement = "X" * max(len(match), 3)
                page.add_redact_annot(
                    rect,
                    text=replacement,
                    fill=(0, 0, 0),        # black box
                    text_color=(1, 1, 1),  # white X's on top
                    fontsize=8,
                )
                total_redactions += 1

        # Actually removes the underlying text/images in the redacted areas
        page.apply_redactions()

    doc.save(output_path)
    doc.close()
    print(f"Done. {total_redactions} item(s) redacted.")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    args = sys.argv[1:]

    # Get the input PDF path — from args, or ask for it.
    if args:
        in_path = args[0]
        extra = args[2:] if len(args) > 2 else []
    else:
        in_path = input("Enter the path to your PDF: ").strip().strip('"')
        extra = []

    if not os.path.isfile(in_path):
        print(f"Couldn't find a file at: {in_path}")
        sys.exit(1)

    # Output path — from args, or auto-generate next to the input file.
    if len(args) > 1:
        out_path = args[1]
    else:
        base, ext = os.path.splitext(in_path)
        out_path = f"{base}_redacted{ext}"

    redact_pdf(in_path, out_path, extra)