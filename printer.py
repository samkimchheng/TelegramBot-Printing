import os
import sys
import subprocess
from pathlib import Path
from PIL import Image
from pypdf import PdfReader

try:
    import win32print
    import win32api
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


def get_default_printer():
    """Get the name of the default Windows printer."""
    if WIN32_AVAILABLE:
        try:
            return win32print.GetDefaultPrinter()
        except Exception as e:
            print(f"Error getting default printer: {e}")
    return "Default Printer (Windows)"


def get_available_printers():
    """List all installed local and network printers."""
    printers = []
    if WIN32_AVAILABLE:
        try:
            flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
            printer_objs = win32print.EnumPrinters(flags)
            for p in printer_objs:
                printers.append(p[2])  # p[2] is the printer name
        except Exception as e:
            print(f"Error enumerating printers: {e}")
    
    default_p = get_default_printer()
    if default_p and default_p not in printers:
        printers.insert(0, default_p)
    return printers, default_p


def count_pdf_pages(file_path):
    """Count pages in a PDF file."""
    try:
        reader = PdfReader(file_path)
        return len(reader.pages)
    except Exception as e:
        print(f"Error counting PDF pages: {e}")
        return 1


def convert_image_to_pdf(image_path: Path, output_pdf_path: Path) -> Path:
    """Convert an image (JPG, PNG, etc.) to a single-page PDF for clean printing."""
    image = Image.open(image_path)
    if image.mode != "RGB":
        image = image.convert("RGB")
    image.save(output_pdf_path, "PDF", resolution=100.0)
    return output_pdf_path


def print_file(file_path: Path, printer_name: str = None, copies: int = 1) -> bool:
    """
    Send file to printer on Windows.
    Uses win32api ShellExecute with 'print' or 'printto' verb.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Ensure file_path is absolute string
    abs_path = str(file_path.resolve())

    # If printer_name is not specified, get default
    if not printer_name:
        printer_name = get_default_printer()

    print(f"Printing {abs_path} to printer: {printer_name} (Copies: {copies})")

    if not WIN32_AVAILABLE:
        print("WIN32 API not available. Cannot send to printer.")
        return False

    success = True
    for c in range(copies):
        try:
            if printer_name and printer_name != "Default Printer (Windows)":
                # 'printto' verb sends file directly to specified printer
                win32api.ShellExecute(
                    0,
                    "printto",
                    abs_path,
                    f'"{printer_name}"',
                    ".",
                    0
                )
            else:
                # 'print' verb sends to default printer
                win32api.ShellExecute(
                    0,
                    "print",
                    abs_path,
                    None,
                    ".",
                    0
                )
        except Exception as e:
            print(f"Error executing print job copy {c+1}: {e}")
            success = False

    return success
