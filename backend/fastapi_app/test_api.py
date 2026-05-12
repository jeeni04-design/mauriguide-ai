"""
Test script for MauriGuide AI API
Run this to test all endpoints
"""

import requests
import json
from pprint import pprint

BASE_URL = "http://127.0.0.1:8001"

def test_health():
    """Test health endpoint"""
    print("\n" + "="*50)
    print("🏥 Testing Health Check")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    pprint(response.json())
    return response.status_code == 200

def test_chat():
    """Test chat endpoint"""
    print("\n" + "="*50)
    print("💬 Testing Chat")
    print("="*50)
    
    messages = [
        "Hello! I'm planning a trip to Mauritius",
        "What are the best beaches?",
        "Tell me about local food",
        "Create a 3-day itinerary for me"
    ]
    
    session_id = None
    
    for msg in messages:
        print(f"\n👤 User: {msg}")
        
        payload = {
            "message": msg,
            "session_id": session_id
        }
        
        response = requests.post(
            f"{BASE_URL}/api/chat/send",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get("session_id")
            print(f"🤖 Assistant: {data['message'][:200]}...")
            if data.get('suggestions'):
                print(f"💡 Suggestions: {data['suggestions']}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    
    return session_id

def test_chat_history(session_id):
    """Test chat history retrieval"""
    print("\n" + "="*50)
    print("📜 Testing Chat History")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/api/chat/history/{session_id}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total messages: {data['count']}")
        print(f"Session exists: {data['exists']}")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        return False

def test_suggestions():
    """Test suggestions endpoint"""
    print("\n" + "="*50)
    print("💡 Testing Suggestions")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/api/chat/suggestions")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Available categories: {data['categories']}")
        print(f"Suggestions: {data['suggestions']}")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        return False

def test_itinerary():
    """Test itinerary generation"""
    print("\n" + "="*50)
    print("🗓️ Testing Itinerary Generation")
    print("="*50)
    
    payload = {
        "days": 3,
        "interests": ["beaches", "food", "culture"],
        "budget": "moderate",
        "travelers": 2,
        "special_requirements": ["vegetarian"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/itinerary/generate",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Title: {data['title']}")
        print(f"Total days: {data['total_days']}")
        print(f"Estimated cost: {data['estimated_cost']}")
        print(f"\nDay 1 Activities:")
        for activity in data['days'][0]['activities']:
            print(f"  - {activity['time']}: {activity['title']}")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return False

def test_recommendations():
    """Test recommendations endpoint"""
    print("\n" + "="*50)
    print("🎯 Testing Recommendations")
    print("="*50)
    
    payload = {
        "category": "beaches",
        "budget": "moderate",
        "limit": 5
    }
    
    response = requests.post(
        f"{BASE_URL}/api/recommendations/get",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total recommendations: {data['total']}")
        print(f"Category: {data['category']}")
        print("\nRecommendations:")
        for place in data['recommendations']:
            print(f"  - {place['name']} (Rating: {place['rating']})")
            print(f"    {place['description'][:100]}...")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return False

def test_recognition():
    """Test image recognition endpoint"""
    print("\n" + "="*50)
    print("🖼️ Testing Image Recognition")
    print("="*50)
    
    # Test with URL (mock)
    response = requests.post(
        f"{BASE_URL}/api/recognition/identify",
        data={"image_url": "https://example.com/image.jpg"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Description: {data['description'][:150]}...")
        print(f"Recognized places: {len(data['recognized_places'])}")
        if data['recognized_places']:
            place = data['recognized_places'][0]
            print(f"  - {place['name']} (Confidence: {place['confidence']})")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return False

def test_landmarks():
    """Test landmarks listing"""
    print("\n" + "="*50)
    print("🏛️ Testing Landmarks List")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/api/recognition/landmarks")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total landmarks: {data['total']}")
        print("\nLandmarks:")
        for landmark in data['landmarks'][:3]:
            print(f"  - {landmark['name']} ({landmark['category']})")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 MAURIGUIDE AI API - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    results = {}
    
    # Test 1: Health Check
    results['health'] = test_health()
    
    # Test 2: Chat
    session_id = test_chat()
    results['chat'] = session_id is not None
    
    # Test 3: Chat History (if chat worked)
    if session_id:
        results['chat_history'] = test_chat_history(session_id)
    
    # Test 4: Suggestions
    results['suggestions'] = test_suggestions()
    
    # Test 5: Itinerary
    results['itinerary'] = test_itinerary()
    
    # Test 6: Recommendations
    results['recommendations'] = test_recommendations()
    
    # Test 7: Image Recognition
    results['recognition'] = test_recognition()
    
    # Test 8: Landmarks
    results['landmarks'] = test_landmarks()
    
    # Print summary
    print("\n" + "="*70)
    print("📊 TEST RESULTS SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.upper():<20} {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\n{'='*70}")
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*70)

if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API")
        print("Make sure the FastAPI server is running:")
        print("  cd fastapi_app")
        print("  uvicorn main:app --reload --port 8001")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")