import os
import sys
import sqlite3
from datetime import datetime

# Keep your existing path logic
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pdf_service import extract_text_from_pdf, analyze_hq_content
from excel_service import extract_data_from_excel, analyze_census_data

def save_to_database(file_name, status, details):
    """Saves the processing results to your db.sqlite3 file."""
    try:
        # Path to your existing sqlite file
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db.sqlite3")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create a simple table if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS broker_logs 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           timestamp TEXT, file_name TEXT, status TEXT, details TEXT)''')
        
        cursor.execute("INSERT INTO broker_logs (timestamp, file_name, status, details) VALUES (?, ?, ?, ?)",
                       (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), file_name, status, str(details)))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ Database Log Failed: {e}")

def generate_email_draft(result, file_name):
    """Turns the raw data into a professional message."""
    if "is_signed" in result: # It's a PDF
        status = "PASSED" if result["clean_pass"] else "FAILED"
        msg = f"Draft: Hi, your PDF {file_name} was processed. Status: {status}."
    elif "total_rows" in result: # It's Excel
        status = "VALID" if result["is_valid"] else "INVALID"
        msg = f"Draft: Census {file_name} checked. Found {result['total_rows']} rows. Status: {status}."
    else:
        status = "ERROR"
        msg = "Draft: Unknown file format."
    
    return status, msg

def process_any_file(file_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    file_path = os.path.join(base_dir, file_name)

    if not os.path.exists(file_path):
        return f"❌ Error: File '{file_name}' not found."

    ext = os.path.splitext(file_name)[1].lower()
    print(f"--- 🤖 AI DECISION: Processing {file_name} ---")

    result = {}
    if ext == ".pdf":
        result = analyze_hq_content(extract_text_from_pdf(file_path))
    elif ext in [".xlsx", ".xls"]:
        df = extract_data_from_excel(file_path)
        result = analyze_census_data(df) if df is not None else {"error": "Excel read failed"}
    
    # 📝 New: Generate Draft and Log to DB
    status, email_draft = generate_email_draft(result, file_name)
    save_to_database(file_name, status, result)
    
    print(f"📩 {email_draft}")
    return result

if __name__ == "__main__":
    # Get the project folder path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    
    print(f"--- 🕵️ AI SCANNING FOLDER: {base_dir} ---")
    
    # List all files and loop through them
    for file in os.listdir(base_dir):
        # Ignore folders, the database, and system files
        if os.path.isfile(os.path.join(base_dir, file)) and not file.endswith(('.py', '.env', '.sqlite3')):
            print(f"\n🚀 Found new file: {file}")
            result = process_any_file(file)
            print(f"Result for {file}: {result}")