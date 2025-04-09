import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, request, jsonify
import os #
from datetime import datetime

# Set up dynamic credentials path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")

# Authenticate Google Sheets
def authenticate_google_sheets():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, scope)
    client = gspread.authorize(creds)
    return client

# Flask setup
app = Flask(__name__)

# Get available promo codes from "Promo_Codes" sheet
def read_codes_from_google():
    client = authenticate_google_sheets()
    sheet = client.open('Promo_Codes').sheet1
    return [row[0] for row in sheet.get_all_values() if row]

# Write used codes to the "Used Codes" sheet
def write_codes_to_google(codes, user_id):
    client = authenticate_google_sheets()
    sheet = client.open('Used Codes').sheet1
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for code in codes:
        sheet.append_row([code.strip(), user_id, timestamp])

# Remove used codes from the "Promo_Codes" sheet
def remove_used_from_google(codes):
    client = authenticate_google_sheets()
    sheet = client.open('Promo_Codes').sheet1
    all_codes = sheet.get_all_values()
    codes_to_remove = set(codes)
    updated_codes = [row for row in all_codes if row[0] not in codes_to_remove]
    sheet.clear()
    sheet.append_rows(updated_codes)

# Check if a code is already used
def is_code_used_from_google(promo_code):
    client = authenticate_google_sheets()
    sheet = client.open('Used Codes').sheet1
    used_codes = [row[0] for row in sheet.get_all_values() if row]
    return promo_code in used_codes

# === API Routes ===
@app.route('/promo-codes', methods=['GET'])
def get_codes():
    count = int(request.args.get('count', 1))
    codes = read_codes_from_google()
    return jsonify(codes[:count])

@app.route('/promo-codes/mark-used', methods=['POST'])
def mark_used():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    codes = data.get('codes', [])
    user_id = data.get('user_id', '')

    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    for code in codes:
        if is_code_used_from_google(code):
            return jsonify({'error': f'Promo code {code} has already been used'}), 400

    write_codes_to_google(codes, user_id)
    remove_used_from_google(codes)

    return jsonify({"status": "success", "used": codes})

#  App Entry Point
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
