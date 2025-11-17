#!/usr/bin/env python3
"""
RTF to Clean Text Converter for "The Traveler's Key"
Extracts and cleans text from RTF file, removing formatting artifacts
and standardizing typography for publication.
"""

import re
import sys


def strip_rtf_control_codes(text):
    """Remove RTF control sequences and extract plain text."""

    # First, handle special RTF escape sequences
    replacements = {
        r"\\rquote": "'",  # Right single quote
        r"\\lquote": "'",  # Left single quote
        r"\\rdblquote": '"',  # Right double quote
        r"\\ldblquote": '"',  # Left double quote
        r"\\emdash": "—",  # Em dash
        r"\\endash": "–",  # En dash
        r"\\'e9": "é",  # e with acute accent
        r"\\'e8": "è",  # e with grave accent
        r"\\'e0": "à",  # a with grave accent
        r"\\'e2": "â",  # a with circumflex
        r"\\'ea": "ê",  # e with circumflex
        r"\\'ee": "î",  # i with circumflex
        r"\\'f4": "ô",  # o with circumflex
        r"\\'fb": "û",  # u with circumflex
        r"\\'e7": "ç",  # c cedilla
        r"\\'a9": "©",  # copyright
        r"\\'85": "…",  # ellipsis
        r"\\tab": "\t",  # tab
        r"\\par": "\n",  # paragraph break
        r"\\line": "\n",  # line break
        r"\\page": "\n\n",  # page break
    }

    for rtf_code, replacement in replacements.items():
        text = re.sub(rtf_code, replacement, text, flags=re.IGNORECASE)

    # Handle generic escaped characters like \'XX (hex codes)
    def hex_replace(match):
        hex_val = match.group(1)
        try:
            return chr(int(hex_val, 16))
        except (ValueError, OverflowError):
            return ""

    text = re.sub(r"\\'([0-9a-f]{2})", hex_replace, text, flags=re.IGNORECASE)

    # Remove RTF control words with parameters (e.g., \fs24, \f42)
    text = re.sub(r'\\[a-z]+\d+', '', text)

    # Remove RTF control words without parameters (e.g., \b, \i, \ul)
    text = re.sub(r'\\[a-z]+\s', ' ', text)

    # Remove RTF control symbols (e.g., \*, \{, \})
    text = re.sub(r'\\[*{}\\]', '', text)

    # Remove remaining backslash commands
    text = re.sub(r'\\[a-z]+', '', text)

    # Remove curly braces (RTF grouping)
    text = re.sub(r'[{}]', '', text)

    # Clean up remaining backslashes
    text = text.replace('\\', '')

    # Remove any remaining RTF-like artifacts
    text = re.sub(r'[a-z]+\d+\s+[a-z]+\d+', ' ', text)

    return text


def fix_escape_characters(text):
    """Fix common escape character issues."""

    # Fix \' followed by letters (likely meant to be just the letter)
    text = re.sub(r"\\'([a-zA-Z])", r"\1", text)

    # Fix \" issues
    text = text.replace('\\"', '"')

    # Fix \* issues (remove them)
    text = text.replace('\\*', '')

    return text


def standardize_quotes(text):
    """Convert straight quotes to proper curly quotes."""

    # First pass: handle double quotes
    # Opening double quote: quote at start of line or after whitespace/punctuation
    text = re.sub(r'(^|[\s\-—\(])"', r'\1"', text, flags=re.MULTILINE)

    # Closing double quote: quote before whitespace, punctuation, or end
    text = re.sub(r'"([\s\.,;:!?\-—\)]|$)', r'"\1', text, flags=re.MULTILINE)

    # Remaining double quotes default to closing quotes
    text = text.replace('"', '"')

    # Second pass: handle single quotes/apostrophes
    # Apostrophes in contractions (keep as right single quote)
    text = re.sub(r"([a-zA-Z])'([a-zA-Z])", r"\1'\2", text)

    # Opening single quote: quote at start or after whitespace
    text = re.sub(r"(^|[\s\-—\(])'", r"\1'", text, flags=re.MULTILINE)

    # Closing single quote: quote before whitespace, punctuation, or end
    text = re.sub(r"'([\s\.,;:!?\-—\)]|$)", r"'\1", text, flags=re.MULTILINE)

    # Remaining single quotes default to right single quote (apostrophe)
    text = text.replace("'", "'")

    return text


def fix_ellipsis_spacing(text):
    """Fix spacing around ellipses."""

    # First, normalize various ellipsis forms to three dots
    text = re.sub(r'\.{3,}', '...', text)
    text = text.replace('…', '...')

    # Remove spaces between the dots
    text = re.sub(r'\.\s*\.\s*\.', '...', text)

    # Ensure space before ellipsis (unless at start of line or after opening quote/paren)
    text = re.sub(r'([^\s\n"\'\(])\.\.\.', r'\1 ...', text)

    # Ensure space after ellipsis (unless at end of line or before closing quote/paren/punctuation)
    text = re.sub(r'\.\.\.([^\s\n"\'\).,;:!?])', r'... \1', text)

    # Clean up multiple spaces
    text = re.sub(r'  +', ' ', text)

    return text


def fix_emdash_spacing(text):
    """Fix spacing around em-dashes (should have no spaces)."""

    # Remove spaces around em-dashes
    text = re.sub(r'\s*—\s*', '—', text)

    # Also handle double-dash if present
    text = re.sub(r'\s*--\s*', '—', text)

    return text


def clean_whitespace(text):
    """Clean up excessive whitespace and line breaks."""

    # Remove RTF artifact codes like "d arsid..."
    text = re.sub(r'\s*d\s+arsid\d+\s*', '\n', text)
    text = re.sub(r'\s*arsid\d+\s*', ' ', text)

    # Remove shape/layout codes
    text = re.sub(r'shapeType\s+\d+.*?fHorizRule\s+\d+', '', text)

    # Remove stray single letters followed by spaces at line ends (RTF artifacts)
    text = re.sub(r'\s+d\s+$', '', text, flags=re.MULTILINE)

    # Fix broken words and lines from RTF formatting
    # RTF often has hard line breaks for display purposes that should be removed

    # First, join obvious mid-word breaks (word split across lines)
    text = re.sub(r'([a-z])-?\n([a-z])', r'\1\2', text)

    # Join lines where the next line starts with lowercase (continuation of sentence)
    # But only if there's a single newline (preserve paragraph breaks)
    text = re.sub(r'([a-z,;])\n([a-z])', r'\1 \2', text)

    # Join lines that end mid-sentence (not with punctuation) with next line
    text = re.sub(r'([a-zA-Z])\nthe ', r'\1 the ', text)
    text = re.sub(r'([a-zA-Z])\nof ', r'\1 of ', text)
    text = re.sub(r'([a-zA-Z])\nin ', r'\1 in ', text)
    text = re.sub(r'([a-zA-Z])\nto ', r'\1 to ', text)
    text = re.sub(r'([a-zA-Z])\nand ', r'\1 and ', text)
    text = re.sub(r'([a-zA-Z])\na ', r'\1 a ', text)
    text = re.sub(r'([a-zA-Z])\nan ', r'\1 an ', text)

    # Fix cases where space was removed when joining lines
    # Add space between lowercase and uppercase (sentence boundaries)
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

    # Ensure proper spacing after common sentence endings that got joined
    text = re.sub(r'\.([A-Z])', r'. \1', text)
    text = re.sub(r'\?([A-Z])', r'? \1', text)
    text = re.sub(r'!([A-Z])', r'! \1', text)

    # Remove trailing whitespace from lines
    text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)

    # Remove leading whitespace from lines (except intentional indents)
    # Keep single tab or 4+ spaces at line start for indentation
    text = re.sub(r'^[ ]{1,3}(?=[^\s])', '', text, flags=re.MULTILINE)

    # Normalize line breaks (max 3 consecutive newlines)
    text = re.sub(r'\n{4,}', '\n\n\n', text)

    # Remove spaces before punctuation
    text = re.sub(r'\s+([.,;:!?])', r'\1', text)

    # Ensure space after punctuation (except in ellipsis)
    text = re.sub(r'([.,;:!?])([A-Za-z])', r'\1 \2', text)

    return text


def extract_main_content(text):
    """Extract only the main book content, removing headers, footers, and TOC."""

    # Remove binary/hex data fields
    text = re.sub(r'[0-9a-f]{64,}', '', text, flags=re.IGNORECASE)

    # Remove PAGEREF codes
    text = re.sub(r'PAGEREF\s+_Toc\d+\s*\\h', '', text)

    # Remove bookmark codes
    text = re.sub(r'_Toc\d+', '', text)

    # Remove field codes like "x0"
    text = re.sub(r'\s+x0\s*', ' ', text)

    # Find where the actual story begins by looking for "Jeff Thorne"
    # which is the start of the first chapter's narrative
    jeff_match = re.search(r"Jeff Thorne'?s alarm clock", text, re.IGNORECASE)

    if jeff_match:
        # Now work backward from Jeff to find the Chapter 1 heading
        before_jeff = text[:jeff_match.start()]
        # Find the last occurrence of "Chapter 1:" before Jeff
        chapter_matches = list(re.finditer(r'Chapter 1:', before_jeff, re.IGNORECASE))
        if chapter_matches:
            # Start from the last "Chapter 1:" before Jeff
            start_pos = chapter_matches[-1].start()
            text = text[start_pos:]
        else:
            # If no Chapter 1 found, just start from Jeff
            text = text[jeff_match.start():]
    else:
        # Fallback: look for any "Chapter 1" followed by actual paragraph content
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if re.match(r'^Chapter\s+1:', line, re.IGNORECASE):
                # Check if the next few lines have substantial content
                next_lines = lines[i+1:i+10]
                content = ' '.join(next_lines)
                # If we find text that looks like narrative (has complete sentences)
                if len(content) > 100 and '.' in content:
                    text = '\n'.join(lines[i:])
                    break

    # Remove trailing artifacts at the end of the document
    # Look for style tables and other RTF metadata that might be at the end
    # Usually these start with patterns like "Normal; heading 1;" or "shapeType"
    text = re.sub(r'\n\s*Normal;\s*heading\s+1;.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'\n\s*shapeType.*$', '', text, flags=re.DOTALL)

    return text


def clean_rtf_file(input_file, output_file):
    """Main function to clean RTF file and save as plain text."""

    print(f"Reading RTF file: {input_file}")

    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            rtf_content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False

    print("Extracting text from RTF...")
    # Step 1: Strip RTF control codes
    text = strip_rtf_control_codes(rtf_content)

    print("Extracting main content...")
    # Step 2: Extract main content (from Chapter 1 onwards)
    text = extract_main_content(text)

    print("Fixing escape characters...")
    # Step 3: Fix escape characters
    text = fix_escape_characters(text)

    print("Standardizing quotation marks...")
    # Step 4: Standardize quotes
    text = standardize_quotes(text)

    print("Fixing ellipsis spacing...")
    # Step 5: Fix ellipsis spacing
    text = fix_ellipsis_spacing(text)

    print("Fixing em-dash spacing...")
    # Step 6: Fix em-dash spacing
    text = fix_emdash_spacing(text)

    print("Cleaning whitespace...")
    # Step 7: Clean whitespace
    text = clean_whitespace(text)

    # Final cleanup
    text = text.strip()

    print(f"Writing cleaned text to: {output_file}")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"✓ Successfully created clean manuscript!")
        print(f"✓ Output file: {output_file}")

        # Print some statistics
        lines = text.split('\n')
        words = len(text.split())
        chars = len(text)
        chapters = len(re.findall(r'Chapter \d+:', text))

        print(f"\nStatistics:")
        print(f"  - Chapters found: {chapters}")
        print(f"  - Total words: {words:,}")
        print(f"  - Total characters: {chars:,}")
        print(f"  - Total lines: {len(lines):,}")

        return True

    except Exception as e:
        print(f"Error writing output file: {e}")
        return False


if __name__ == "__main__":
    input_file = "/home/user/Travelers_Tail_Book/Travlers key.rtf"
    output_file = "/home/user/Travelers_Tail_Book/The_Travelers_Key_Clean.txt"

    success = clean_rtf_file(input_file, output_file)

    if success:
        print("\n✓ Cleaning complete!")
        sys.exit(0)
    else:
        print("\n✗ Cleaning failed!")
        sys.exit(1)
