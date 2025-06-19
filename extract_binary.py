#!/usr/bin/env python3
"""
extract_binary.py - Reconstruct binary executable from decimal dump

This script reads a text file containing decimal values (typically extracted
from malicious VBA macro payloads using `WriteBytes objFile, ...`) and
reconstructs the binary executable from those values.

Use case:
- Common in malware reverse engineering when macros write EXEs in obfuscated decimal format.
- Converts human-readable decimal into a PE binary.

Author: Felix1862
GitHub: https://github.com/Felix1862
License: MIT
"""

def extract_binary_from_writebytes(input_file: str, output_file: str) -> None:
    """
    Extracts and reconstructs a binary file from decimal byte values
    stored in a text file.

    Args:
        input_file (str): Path to the input file containing space-separated decimal byte values.
        output_file (str): Path where the reconstructed binary file should be saved.

    Returns:
        None
    """
    try:
        # Open and read the input file (e.g., dump_data.txt)
        with open(input_file, 'r') as f:
            # Join lines into one string, separating values with space
            content = f.read().replace('\n', ' ')

        # Convert each valid decimal string to an integer (byte)
        byte_values = [int(b) for b in content.split() if b.isdigit()]

        # Write the byte values to a binary output file
        with open(output_file, 'wb') as out:
            out.write(bytearray(byte_values))

        print(f"[+] Binary written to {output_file}")

    except FileNotFoundError:
        print(f"[!] File not found: {input_file}")
    except ValueError:
        print("[!] Malformed byte values detected. Ensure only integers are present.")
    except Exception as e:
        print(f"[!] Unexpected error: {e}")



if __name__ == "__main__":
    # Example usage — can be replaced with argparse for CLI use
    extract_binary_from_writebytes("dump_data.txt", "file.exe")
