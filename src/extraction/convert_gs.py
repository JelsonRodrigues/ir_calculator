import glob
import os
import ghostscript as gs

# Convert a single pdf file to pdf with ghostscript
def convert_file_with_ghostscript(file_path: str) -> bool:
    if not os.path.isfile(file_path):
        return False

    output_path = f'{file_path}.converted'
    args = [
        "ps2pdf",                       # The ps2pdf utility converts Postscript format to Adobe PDF
        "-dNOPAUSE",                    # No pause after each page
        "-dBATCH",                      # Don't prompt for user input
        "-dQUIET",                      # Suppress any messages
        "-dSAFER",                      # Safe mode
        "-r300",                        # Resolution is 300 ppi
        "-sDEVICE=pdfwrite",            # Use the pdfwrite device
        f"-sOutputFile={output_path}",  # Output file
        "-f", file_path,                # Input file
    ]

    gs.Ghostscript(*args)

    # Swap original and converted files
    os.remove(file_path)
    os.rename(f'{output_path}', f'{file_path}')

    return True

# Convert all PDF files in a directory
def convert_path_with_ghostscript(path: str) -> bool:
    if not os.path.isdir(path):
        return False

    pdf_files = glob.glob(f'{path}/*.pdf')

    return all(map(convert_file_with_ghostscript, pdf_files))
