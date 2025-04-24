import requests
import json

BASE_URL = 'http://localhost:8000/api'

# Test creating a new course schedule
def test_create_schedule():
    print("Testing schedule creation...")
    url = f"{BASE_URL}/schedules/create/"
    
    data = {
        "course_code": "CMSC 126",
        "section": "A",
        "type": "Lecture",
        "room": "SCI 405",
        "day": "M TH",
        "time": "11:00 AM - 12:00 PM"
    }
    
    response = requests.post(url, json=data)
    
    if response.status_code == 201:
        print("Schedule created successfully!")
        print(json.dumps(response.json(), indent=4))
        return response.json()
    else:
        print(f"Failed to create schedule. Status code: {response.status_code}")
        print(response.text)
        return None

# Test getting all courses
def test_get_courses():
    print("\nTesting get all courses...")
    url = f"{BASE_URL}/courses/"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        print("Courses retrieved successfully!")
        courses = response.json()
        print(f"Found {len(courses)} courses")
        return courses
    else:
        print(f"Failed to get courses. Status code: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    print("API Test Script")
    print("===============")
    
    # Create a schedule
    course = test_create_schedule()
    
    # Get all courses
    courses = test_get_courses()
    
    print("\nTest completed!") 