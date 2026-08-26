# Sensitive Info Classifier (PDF Redactor)

A Python tool that scans any PDF for sensitive information and permanently redacts it — the underlying text is removed (not just visually covered), so the original data can't be recovered by copy-pasting or re-extracting text.

## Features

Detects and redacts the following via regex:

- Email addresses
- Phone numbers (Indian mobile + general international/US formats)
- SSNs (US format)
- Credit/debit card numbers
- Aadhaar numbers (Indian ID)
- IP addresses
- IFSC codes (Indian bank routing codes)
- Customer/account IDs
- CVV (when labeled)
- Card expiry dates
- PAN card numbers (Indian tax ID)

Each match is replaced with a black box containing `X`'s, and the original text is stripped from the PDF using PyMuPDF's redaction API.

## Installation

```bash
pip install pymupdf
```

## Usage

Run interactively — it will prompt for a file path:

```bash
python 01.py
```

Or pass arguments directly:

```bash
python 01.py input.pdf
python 01.py input.pdf output.pdf
python 01.py input.pdf output.pdf "John Doe" "Acme Corp"
```

The last two examples show how to pass extra custom terms (names, company names, etc.) to redact beyond what the regex patterns catch.

Output is saved as `<input>_redacted.pdf` by default, or to the path you specify.

## How it works

1. Extracts text from each PDF page.
2. Matches sensitive patterns using the regex rules in `PATTERNS`.
3. Locates each match's position on the page and applies a redaction annotation (black box + white `X`s).
4. Calls `apply_redactions()` to permanently remove the underlying text/images in those areas.
5. Saves the cleaned PDF.

## Notes

- Add or remove patterns in the `PATTERNS` dictionary to customize detection.
- Use the `CUSTOM_TERMS` list (or CLI args) to redact specific literal strings not covered by regex.
- Broad patterns (e.g. generic phone/card number formats) can occasionally over-match — review output for false positives on sensitive documents.
