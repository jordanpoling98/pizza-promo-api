import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, request, jsonify
import os
from datetime import datetime

# Authenticate Google Sheets
def authenticate_google_sheets():
    # Define the scope of access you need (Sheets and Drive API)
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
    
    # Authenticate with the credentials.json file
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, scope)
    
    # Authorize and create a client
    client = gspread.authorize(creds)
    
    return client


app = Flask(__name__)

CSV_FILE = 'promo_codes.csv'
USED_FILE = 'used_codes.csv'

# Read codes from Google Sheets (Promo_Codes)
def read_codes_from_google():
    client = authenticate_google_sheets()
    
    # Open the Google Sheet by its name (change this to your sheet name)
    sheet = client.open('Promo_Codes').sheet1  # Adjust 'Promo_Codes' to your sheet name
    
    # Get all the values in the first column (promo codes)
    return [row[0] for row in sheet.get_all_values() if row]  # Adjust based on your sheet structure

# Function to write used codes to Google Sheets
def write_codes_to_google(codes, user_id):
    client = authenticate_google_sheets()
    
    # Open the "Used Codes" sheet (replace with your actual sheet name)
    sheet = client.open('Used Codes').sheet1  # Adjust to your sheet name
    
    for code in codes:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Append the promo code, user ID, and timestamp to the Google Sheet
        sheet.append_row([code.strip(), user_id, timestamp])  # Adjust based on your sheet structure


# Function to remove used codes from Google Sheets (for multiple codes)
def remove_used_from_google(codes):
    client = authenticate_google_sheets()
    
    # Open the "Promo_Codes" sheet (replace with your actual sheet name)
    sheet = client.open('Promo_Codes').sheet1  # Adjust to your promo codes sheet name
    
    # Get all the current codes from the first column
    all_codes = sheet.get_all_values()  # Get all rows of the sheet
    
    # Filter out the used codes
    codes_to_remove = set(codes)
    updated_codes = [row for row in all_codes if row[0] not in codes_to_remove]
    
    # Clear the sheet and rewrite the remaining codes
    sheet.clear()  # Clears the existing sheet data
    sheet.append_rows(updated_codes)  # Rewrites the remaining (non-used) codes

# Function to check if a code has already been used
def is_code_used_from_google(promo_code):
    client = authenticate_google_sheets()
    
    # Open the "Used Codes" sheet (replace with the actual name if it's different)
    sheet = client.open('Used Codes').sheet1 
    
    # Get all rows from the sheet
    used_codes = [row[0] for row in sheet.get_all_values() if row]
    
    # Check if the promo code is in the used codes list
    return promo_code in used_codes

@app.route('/promo-codes', methods=['GET'])
def get_codes():
    count = int(request.args.get('count', 1))
    codes = read_codes_from_google()
    return jsonify(codes[:count])

@app.route('/promo-codes/mark-used', methods=['POST'])
def mark_used():
    data = request.get_json()  # Get the incoming JSON data
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400  # Check if JSON is empty or invalid
    
    codes = data.get('codes', [])
    user_id = data.get('user_id', '')  # Ensure user_id is sent

    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400  # Check if user_id exists
    
    print(f"Received codes: {codes}")
    print(f"User ID: {user_id}")

    # Check if the promo code has already been used in Google Sheets
    for code in codes:
        if is_code_used_from_google(code):  # This function checks if the code is used already
            return jsonify({'error': f'Promo code {code} has already been used'}), 400
    
    # Write the used codes to Google Sheets
    write_codes_to_google(codes, user_id)

    # Remove the used codes from Google Sheets
    remove_used_from_google(codes)

    return jsonify({"status": "success", "used": codes})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
