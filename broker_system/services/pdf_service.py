import pdfplumber
import os

def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text
def analyze_hq_content(text):
    """
    Looks for red flags in the extracted text.
    """
    text = text.lower()
    
    # 1. Check for signatures/dates
    is_signed = "signature" in text or "dated" in text
    
    # 2. Look for medical 'Red Flags'
    red_flags = ["surgery", "diabetes", "heart", "cancer", "medication", "injury"]
    found_issues = [word for word in red_flags if word in text]
    
    return {
            "is_signed": is_signed,
            "red_flags_found": found_issues,
            "clean_pass": not found_issues and is_signed
        }

# --- THIS PART MUST START AT THE VERY EDGE OF THE LEFT MARGIN ---
if __name__ == "__main__":
    import os
    # Find the main project folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    
    print(f"--- SCANNING DIRECTORY: {base_dir} ---")
    files_in_folder = os.listdir(base_dir)
    print(f"Files found: {files_in_folder}")

    # Let's try to find a PDF that starts with '367'
    target_file = None
    for f in files_in_folder:
        if f.startswith("367") and f.lower().endswith(".pdf"):
            target_file = os.path.join(base_dir, f)
            break

    if target_file:
        print(f"--- ✅ MATCH FOUND: {target_file} ---")
        raw_text = extract_text_from_pdf(target_file)
        print("--- AI READ THE FOLLOWING (Preview) ---")
        print(raw_text[:300])
        
        analysis = analyze_hq_content(raw_text)
        print("\n--- BROKER AI ANALYSIS ---")
        print(f"Signature Detected: {analysis['is_signed']}")
        print(f"Red Flags: {analysis['red_flags_found']}")
    else:
        print("❌ No PDF starting with '367' was found in the main folder.")