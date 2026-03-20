import pdfplumber
import pandas as pd
import sys

print(f"--- Python Version: {sys.version} ---")

try:
    # Test 1: PDFPlumber
    print("Testing PDFPlumber...")
    # This just checks if the library is 'reachable'
    test_pdf = pdfplumber.PDF
    print("✅ PDFPlumber is working!")
except Exception as e:
    print(f"❌ PDFPlumber Error: {e}")

try:
    # Test 2: Pandas
    print("\nTesting Pandas...")
    df = pd.DataFrame({"Goal": ["Build AI"], "Status": ["In Progress"]})
    print(df)
    print("✅ Pandas is working!")
except Exception as e:
    print(f"❌ Pandas Error: {e}")