"""
End-to-End Test Script
Verifies: Auth, Upload, Chat
"""
import requests
import sys
import os
import time

BASE_URL = "http://localhost:8000"
USER_EMAIL = f"test_{int(time.time())}@example.com"
USER_PASSWORD = "password123"

# Paths to test files
DISCHARGE_PDF = r"c:\Users\harsh\OneDrive\Desktop\Nik\GIG\docs\discharge_summaries\discharge_summ_pdf_2.pdf"
BILL_PDF = r"c:\Users\harsh\OneDrive\Desktop\Nik\GIG\docs\bills\No_OC_Bill2.pdf"

def print_pass(msg):
    print(f"✅ PASS: {msg}")

def print_fail(msg, details=""):
    print(f"❌ FAIL: {msg}")
    if details:
        print(f"   Details: {details}")
    # Don't exit, try to continue
    # sys.exit(1)

def test_health():
    try:
        r = requests.get(f"{BASE_URL}/")
        if r.status_code == 200:
            print_pass(f"Server is running ({r.json()})")
        else:
            print_fail(f"Server returned {r.status_code}")
    except Exception as e:
        print_fail("Could not connect to server", str(e))
        sys.exit(1)

def test_auth():
    # 1. Signup
    print(f"\nTesting Auth with {USER_EMAIL}...")
    print(f"  Signup user: {USER_EMAIL}")
    signup_data = {
        "email": USER_EMAIL,
        "password": USER_PASSWORD,
        "full_name": "Test User"
    }
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    
    if response.status_code == 201:
        print("✅ PASS: Signup successful")
    elif response.status_code == 400 and "already exists" in response.text:
         print("⚠️  WARN: User already exists, proceeding to login")
    else:
        print(f"❌ FAIL: Signup failed {response.status_code}")
        print(f"   Details: {response.text}")
        return

    # 2. Login
    login_data = {
        "username": USER_EMAIL,
        "password": USER_PASSWORD
    }
    r = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if r.status_code == 200:
        token = r.json()["access_token"]
        print_pass("Login successful, got token")
        return token
    else:
        print_fail("Login failed", r.text)
        return None

def test_upload(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # Upload Discharge Summary
    if os.path.exists(DISCHARGE_PDF):
        print(f"\nUploading Discharge Summary: {DISCHARGE_PDF}...")
        with open(DISCHARGE_PDF, "rb") as f:
            files = {"file": ("discharge.pdf", f, "application/pdf")}
            r = requests.post(f"{BASE_URL}/upload/discharge", headers=headers, files=files)
            if r.status_code == 200:
                print_pass(f"Discharge upload successful (ID: {r.json().get('id')})")
            else:
                print_fail("Discharge upload failed", r.text)
    else:
        print_fail(f"Test file not found: {DISCHARGE_PDF}")

    # Wait for processing (it's a background task)
    print("Waiting 5s for background processing...")
    time.sleep(5)

def test_chat(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    queries = [
        "Explain my diagnosis.",
        "What medicines are prescribed?",
    ]
    
    print("\nTesting Chat Agents...")
    for q in queries:
        print(f"  User: {q}")
        payload = {"message": q}
        try:
            # Increase timeout for slow RAG
            r = requests.post(f"{BASE_URL}/chat/", json=payload, headers=headers, timeout=60)
            if r.status_code == 200:
                resp = r.json()
                print_pass(f"Got response ({resp['intent_detected']}): {resp['response'][:100]}...")
            else:
                print_fail(f"Chat failed for '{q}'", r.text)
        except Exception as e:
            print_fail(f"Chat error for '{q}'", str(e))

if __name__ == "__main__":
    print("Starting E2E Tests...")
    test_health()
    token = test_auth()
    if token:
        test_upload(token)
        test_chat(token)
    print("\nTests Completed.")
