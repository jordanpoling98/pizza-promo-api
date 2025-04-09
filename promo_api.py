import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, request, jsonify
import os
from datetime import datetime

# Set up dynamic credentials path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = "/etc/secrets/credentials.json"

def authenticate_google_sheets():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, scope)
    client = gspread.authorize(creds)
    return client

# Flask app initialization
app = Flask(__name__)

def read_codes_from_google():
    client = authenticate_google_sheets()
    sheet = client.open('Promo_Codes').sheet1
    all_values = sheet.get_all_values()
    # Filter out any empty rows
    codes = [row[0] for row in all_values if row and row[0]]
    return codes

def write_codes_to_google(codes, user_id):
    client = authenticate_google_sheets()
    sheet = client.open('Used Codes').sheet1
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for code in codes:
        # Ensure extra whitespace is removed and then append the row
        sheet.append_row([code.strip(), user_id, timestamp])

def remove_used_from_google(codes):
    client = authenticate_google_sheets()
    sheet = client.open('Promo_Codes').sheet1
    all_values = sheet.get_all_values()
    codes_to_remove = set(codes)
    updated_codes = [row for row in all_values if row and row[0] not in codes_to_remove]
    # Clear the sheet and write back the updated codes if any exist
    sheet.clear()
    if updated_codes:
        sheet.append_rows(updated_codes)

def is_code_used_from_google(promo_code):
    client = authenticate_google_sheets()
    sheet = client.open('Used Codes').sheet1
    used_codes = [row[0] for row in sheet.get_all_values() if row]
    return promo_code in used_codes

# === API Routes ===

@app.route('/promo-codes', methods=['GET'])
def get_codes():
    try:
        count = int(request.args.get('count', 1))
    except ValueError:
        count = 1
    codes = read_codes_from_google()
    return jsonify(codes[:count])

@app.route('/promo-codes/mark-used', methods=['POST'])
def mark_used():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    codes = data.get('codes', [])
    user_id = data.get('user_id', 'anonymous')  # Default to "anonymous" if not provided

    if not isinstance(codes, list) or not codes:
        return jsonify({'error': 'Promo codes must be a non-empty list'}), 400

    # Check if any are already used
    for code in codes:
        if is_code_used_from_google(code):
            return jsonify({'error': f'Promo code {code} has already been used'}), 400

    write_codes_to_google(codes, user_id)
    remove_used_from_google(codes)

    return jsonify({"status": "success", "used": codes})


# App entry point
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
