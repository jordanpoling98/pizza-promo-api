import requests

# Test POST request to mark codes as used
def test_post_mark_used():
    data = {
        "codes": ["ds53dkk6vcxz", "dxk5h7t3y4xz"],  # Example promo codes
        "user_id": "user123"  # You can change this to any user ID
    }
    
    print(f"Sending request with data: {data}")  # Debug log to check the request data
    
    response = requests.post("http://127.0.0.1:10000/promo-codes/mark-used", json=data)
    
    print(f"Response: {response.status_code}")  # Debug log to check the response status
    if response.status_code == 200:
        print("POST /promo-codes/mark-used response:")
        print(response.json())  # Should display success message or error
    else:
        print(f"Failed to mark codes as used: {response.status_code}")

if __name__ == "__main__":
    print("Testing POST /promo-codes/mark-used")
    test_post_mark_used()
