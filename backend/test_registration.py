import requests
import json

DJANGO_URL = "http://127.0.0.1:8000"

print("="*70)
print("Testing Django Registration Endpoint")
print("="*70)

register_data = {
    "username": "mauriguide_test",
    "email": "test@mauriguide.com",
    "password": "secure123456",
    "first_name": "Mauri",
    "last_name": "Guide"
}

print("\n📤 Sending registration request...")
print(f"URL: {DJANGO_URL}/api/auth/register/")
print(f"Data: {json.dumps(register_data, indent=2)}")

try:
    response = requests.post(
        f"{DJANGO_URL}/api/auth/register/",
        json=register_data,
        timeout=10
    )
    
    print(f"\n📥 Response Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    try:
        print(f"\n📄 Response Body:")
        print(json.dumps(response.json(), indent=2))
    except:
        print(f"Raw Response: {response.text}")
    
    if response.status_code == 201:
        print("\n✅ Registration successful!")
    elif response.status_code == 400:
        print("\n⚠️  User might already exist. Let's try login...")
        
        login_response = requests.post(
            f"{DJANGO_URL}/api/auth/login/",
            json={
                "username": register_data['username'],
                "password": register_data['password']
            }
        )
        
        print(f"\n📥 Login Status: {login_response.status_code}")
        print(f"Login Response:")
        print(json.dumps(login_response.json(), indent=2))
    else:
        print(f"\n❌ Registration failed with status {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ Cannot connect to Django server!")
    print("Make sure Django is running: python manage.py runserver")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()