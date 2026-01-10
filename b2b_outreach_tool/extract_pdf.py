from pypdf import PdfReader
import sys

def extract_text(file_path, max_pages=10):
    try:
        reader = PdfReader(file_path)
        num_pages = len(reader.pages)
        print(f"Total pages: {num_pages}")
        
        text = ""
        pages_to_read = min(max_pages, num_pages)
        for i in range(pages_to_read):
            page_text = reader.pages[i].extract_text()
            text += f"\n--- Page {i+1} ---\n{page_text}\n"
        
        return text
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_pdf.py <file_path>")
    else:
        content = extract_text(sys.argv[1])
        print(content)
