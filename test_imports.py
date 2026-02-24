import os
print("Testing google.genai import...")
try:
    from google import genai
    from google.genai import types
    print("Import successful!")
    client = genai.Client(api_key="TEST")
    print("Client init successful!")
except Exception as e:
    print(f"FAILED: {e}")
