#!/usr/bin/env python3
"""
Convert SRT subtitle files to plain text for speech-to-text evaluation.
Removes timestamps and sequence numbers, preserving only the transcript content.
"""

import sys
import re
from pathlib import Path


def srt_to_plaintext(srt_path, output_path=None, join_fragments=True):
    """
    Convert SRT file to plain text.

    Args:
        srt_path: Path to input SRT file
        output_path: Path to output text file (optional)
        join_fragments: If True, join lines within each subtitle block

    Returns:
        Plain text string
    """
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove BOM if present
    content = content.lstrip('\ufeff')

    # Split into subtitle blocks (separated by blank lines)
    blocks = re.split(r'\n\s*\n', content.strip())

    text_lines = []

    for block in blocks:
        lines = block.strip().split('\n')

        # Skip empty blocks
        if not lines:
            continue

        # First line is sequence number, second is timestamp
        # Everything after that is the actual text
        text_content = []
        for line in lines[2:]:  # Skip first two lines
            line = line.strip()
            if line:
                text_content.append(line)

        if text_content:
            if join_fragments:
                # Join all lines in this subtitle block
                text_lines.append(' '.join(text_content))
            else:
                # Keep lines separate
                text_lines.extend(text_content)

    # Join all text with spaces
    plain_text = ' '.join(text_lines)

    # Optional: Clean up multiple spaces
    plain_text = re.sub(r'\s+', ' ', plain_text).strip()

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(plain_text)
        print(f"Converted: {srt_path} -> {output_path}")

    return plain_text


def main():
    if len(sys.argv) < 2:
        print("Usage: python srt_to_text.py <input.srt> [output.txt]")
        print("\nIf output file is not specified, will create .txt file alongside .srt")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    # Determine output path
    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
    else:
        output_path = input_path.with_suffix('.txt')

    # Convert
    text = srt_to_plaintext(input_path, output_path)

    # Print stats
    word_count = len(text.split())
    char_count = len(text)
    print(f"\nStats:")
    print(f"  Words: {word_count}")
    print(f"  Characters: {char_count}")


if __name__ == '__main__':
    main()
