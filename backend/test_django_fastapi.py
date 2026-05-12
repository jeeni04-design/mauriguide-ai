"""
Complete Django <-> FastAPI Integration Test
"""
import requests
import json

DJANGO_URL = "http://127.0.0.1:8000"
FASTAPI_URL = "http://127.0.0.1:8001"

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def test_django_health():
    """Test Django API health"""
    print_header("1. Testing Django API Health")
    
    try:
        response = requests.get(f"{DJANGO_URL}/api/health/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success("Django API is healthy")
            print_info(f"Service: {data.get('service')}")
            print_info(f"Message: {data.get('message')}")
            return True
        else:
            print_error(f"Django health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Cannot connect to Django: {e}")
        return False

def test_fastapi_health():
    """Test FastAPI health"""
    print_header("2. Testing FastAPI Health")
    
    try:
        response = requests.get(f"{FASTAPI_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success("FastAPI is healthy")
            print_info(f"Service: {data.get('service')}")
            print_info(f"Version: {data.get('version')}")
            return True
        else:
            print_error(f"FastAPI health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Cannot connect to FastAPI: {e}")
        return False

def test_user_registration():
    """Test user registration"""
    print_header("3. Testing User Registration")
    
    register_data = {
        "username": "mauriguide_test",
        "email": "test@mauriguide.com",
        "password": "secure123456",
        "first_name": "Mauri",
        "last_name": "Guide"
    }
    
    try:
        response = requests.post(
            f"{DJANGO_URL}/api/auth/register/",
            json=register_data,
            timeout=5
        )
        
        if response.status_code == 201:
            data = response.json()
            print_success("User registered successfully")
            print_info(f"Username: {data['username']}")
            print_info(f"User ID: {data['user_id']}")
            print_info(f"Token: {data['token'][:30]}...")
            return data['token']
        elif response.status_code == 400:
            # User might already exist, try login
            print_info("User already exists, attempting login...")
            return test_user_login(register_data['username'], register_data['password'])
        else:
            print_error(f"Registration failed: {response.text}")
            return None
    except Exception as e:
        print_error(f"Registration error: {e}")
        return None

def test_user_login(username, password):
    """Test user login"""
    print_header("4. Testing User Login")
    
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(
            f"{DJANGO_URL}/api/auth/login/",
            json=login_data,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Login successful")
            print_info(f"Username: {data['username']}")
            print_info(f"Token: {data['token'][:30]}...")
            return data['token']
        else:
            print_error(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print_error(f"Login error: {e}")
        return None

def test_token_verification(token):
    """Test token verification in Django"""
    print_header("5. Testing Token Verification (Django)")
    
    try:
        response = requests.get(
            f"{DJANGO_URL}/api/auth/verify/",
            headers={"Authorization": f"Token {token}"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Token verified in Django")
            print_info(f"User ID: {data['user_id']}")
            print_info(f"Username: {data['username']}")
            print_info(f"Email: {data['email']}")
            return True
        else:
            print_error(f"Token verification failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Verification error: {e}")
        return False

def test_authenticated_chat(token):
    """Test authenticated chat with FastAPI"""
    print_header("6. Testing Authenticated Chat (FastAPI)")
    
    try:
        response = requests.post(
            f"{FASTAPI_URL}/api/chat/send",
            json={"message": "Hello! I'm planning a trip to Mauritius. What beaches do you recommend?"},
            headers={"Authorization": f"Token {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Authenticated chat successful")
            print_info(f"Session ID: {data['session_id']}")
            print_info(f"Authenticated: {data['metadata']['authenticated']}")
            print_info(f"Response preview: {data['message'][:100]}...")
            if data.get('suggestions'):
                print_info(f"Suggestions: {', '.join(data['suggestions'][:2])}...")
            return data['session_id']
        else:
            print_error(f"Chat request failed: {response.status_code}")
            print_error(response.text)
            return None
    except Exception as e:
        print_error(f"Chat error: {e}")
        return None

def test_unauthenticated_chat():
    """Test unauthenticated chat"""
    print_header("7. Testing Unauthenticated Chat (FastAPI)")
    
    try:
        response = requests.post(
            f"{FASTAPI_URL}/api/chat/send",
            json={"message": "What are the best beaches in Mauritius?"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Unauthenticated chat works")
            print_info(f"Authenticated: {data['metadata']['authenticated']}")
            print_info(f"Response preview: {data['message'][:100]}...")
            return True
        else:
            print_error(f"Unauthenticated chat failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_itinerary_generation(token):
    """Test itinerary generation"""
    print_header("8. Testing Itinerary Generation (FastAPI)")
    
    try:
        response = requests.post(
            f"{FASTAPI_URL}/api/itinerary/generate",
            json={
                "days": 3,
                "interests": ["beaches", "food", "culture"],
                "budget": "moderate",
                "travelers": 2
            },
            headers={"Authorization": f"Token {token}"} if token else {},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Itinerary generated successfully")
            print_info(f"Title: {data['title']}")
            print_info(f"Days: {data['total_days']}")
            print_info(f"Estimated cost: {data['estimated_cost']}")
            print_info(f"Day 1 activities: {len(data['days'][0]['activities'])}")
            return True
        else:
            print_error(f"Itinerary generation failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def run_all_tests():
    """Run complete integration test suite"""
    print("\n" + "🧪 "*35)
    print("  MAURIGUIDE AI - DJANGO <-> FASTAPI INTEGRATION TEST")
    print("🧪 "*35)
    
    results = {}
    token = None
    
    # Test 1: Django Health
    results['django_health'] = test_django_health()
    if not results['django_health']:
        print_error("\n⚠️  Django is not running! Start it with:")
        print_error("   cd django_app")
        print_error("   python manage.py runserver")
        return
    
    # Test 2: FastAPI Health
    results['fastapi_health'] = test_fastapi_health()
    if not results['fastapi_health']:
        print_error("\n⚠️  FastAPI is not running! Start it with:")
        print_error("   cd fastapi_app")
        print_error("   uvicorn main:app --reload --port 8001")
        return
    
    # Test 3: User Registration
    token = test_user_registration()
    results['registration'] = token is not None
    
    # Test 4: Token Verification
    if token:
        results['token_verification'] = test_token_verification(token)
    
    # Test 5: Authenticated Chat
    if token:
        session_id = test_authenticated_chat(token)
        results['authenticated_chat'] = session_id is not None
    
    # Test 6: Unauthenticated Chat
    results['unauthenticated_chat'] = test_unauthenticated_chat()
    
    # Test 7: Itinerary Generation
    results['itinerary'] = test_itinerary_generation(token)
    
    # Print Summary
    print_header("TEST SUMMARY")
    
    total = len(results)
    passed = sum(results.values())
    
    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"{test_name.upper():<30} {status}")
    
    print("\n" + "="*70)
    print(f"  TOTAL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*70)
    
    if passed == total:
        print("\n🎉 All tests passed! Django and FastAPI are fully integrated! 🎉\n")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.\n")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")