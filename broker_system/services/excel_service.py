import pandas as pd
import os

def extract_data_from_excel(file_path):
    try:
        # 1. Load the raw file
        df_raw = pd.read_excel(file_path, header=None)
        
        # 2. Find the row that contains "Name of Member" or "اسم الشخص"
        header_row = 0
        for i, row in df_raw.iterrows():
            # Convert the whole row to one long string to search it
            row_content = " ".join([str(val).lower() for val in row.values if pd.notna(val)])
            if "name of member" in row_content or "اسم الشخص" in row_content:
                header_row = i
                break
        
        # 3. Re-read the file starting from that found header row
        df = pd.read_excel(file_path, skiprows=header_row)
        return df
    except Exception as e:
        print(f"❌ Error reading Excel: {e}")
        return None

def analyze_census_data(df):
    # 1. FIND THE NAME COLUMN NAME
    # We need to know which column to check for "Empty"
    name_col = None
    for col in df.columns:
        if any(key in str(col).lower() for key in ["name", "اسم", "first"]):
            name_col = col
            break

    # 2. FILTER OUT GHOST ROWS
    if name_col:
        # This keeps only rows where the Name is NOT empty and is NOT a title
        df = df[df[name_col].notna()]
        # Filter out rows that are just 'First (الاسم)' or header repeats
        df = df[~df[name_col].astype(str).str.contains("Name|الاسم", na=False)]

    # 3. GET ACTUAL COUNT
    total_members = len(df)

    # 4. REST OF YOUR LOGIC
    actual_cols = [str(c).replace('\n', ' ').strip().lower() for c in df.columns]
    checks = {
        "Name": ["name", "اسم", "first"],
        "Date of Birth": ["birth", "dob", "تاريخ الميلاد"],
        "Gender": ["gender", "sex", "الجنس"],
        "ID Number": ["iqama", "id", "national", "رقم الهوية"]
    }
    
    missing = []
    for official_name, keywords in checks.items():
        if not any(any(key in col for key in keywords) for col in actual_cols):
            missing.append(official_name)

    return {
        "total_rows": total_members,
        "missing_columns": missing,
        "is_valid": len(missing) == 0
    }
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    
    # 🕵️ Auto-find ANY Excel file in the main folder
    files_in_folder = os.listdir(base_dir)
    target_file = None
    
    for f in files_in_folder:
        if f.lower().endswith(('.xlsx', '.xls')):
            target_file = os.path.join(base_dir, f)
            break

    if target_file:
        print(f"--- ✅ MATCH FOUND: {os.path.basename(target_file)} ---")
        data = extract_data_from_excel(target_file)
        
        if data is not None:
            print("--- DATA PREVIEW ---")
            print(data.head()) 
            
            report = analyze_census_data(data)
            print("\n--- BROKER AI QUALITY CHECK ---")
            print(f"Total Members Found: {report['total_rows']}")
            
            if report['is_valid']:
                print("✅ STATUS: All required columns found.")
            else:
                print(f"⚠️ STATUS: Missing columns: {report['missing_columns']}")
    else:
        print(f"❌ No Excel files found in: {base_dir}")