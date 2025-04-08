import requests

# Test GET request for promo codes
response = requests.get("http://localhost:10000/promo-codes?count=5")
print(response.json())  # Should display the promo codes

# Test POST request to mark codes as used
data = {
    "codes": ["DISCOUNT2025"],
    "user_id": "user123"
}

response = requests.post("http://localhost:10000/promo-codes/mark-used", json=data)
print(response.json())  # Should display success message or error
