from flask import Flask, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)

CSV_FILE = 'promo_codes.csv'
USED_FILE = 'used_codes.csv'

# Read codes from a file (removes BOMs + strips lines)
def read_codes(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, 'r', encoding='utf-8-sig') as f:
        return [line.strip() for line in f if line.strip()]

# Write used codes to file with user_id and timestamp
def write_codes(filename, codes, user_id):
    try:
        with open(filename, 'a', encoding='utf-8') as f:
            for code in codes:
                # Writing the promo code along with user ID and timestamp
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"{code.strip()},{user_id},{timestamp}\n")
    except PermissionError:
        print(f"⚠️ Cannot write to {filename}. File may be open elsewhere.")

# Remove used codes from promo_codes.csv
def remove_used(codes):
    if not os.path.exists(CSV_FILE):
        return

    used_set = set(code.strip() for code in codes)  # Normalize
    with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
        all_codes = [line.strip() for line in f if line.strip()]

    remaining = [code for code in all_codes if code not in used_set]

    with open(CSV_FILE, 'w', encoding='utf-8') as f:
        for code in remaining:
            f.write(code + '\n')

# Function to check if a code has already been used
def is_code_used(promo_code):
    if not os.path.exists(USED_FILE):
        return False

    with open(USED_FILE, 'r', encoding='utf-8') as f:
        used_codes = [line.split(',')[0].strip() for line in f]
    return promo_code in used_codes

@app.route('/promo-codes', methods=['GET'])
def get_codes():
    count = int(request.args.get('count', 1))
    codes = read_codes(CSV_FILE)
    return jsonify(codes[:count])

@app.route('/promo-codes/mark-used', methods=['POST'])
def mark_used():
    data = request.get_json()
    codes = data.get('codes', [])
    user_id = data.get('user_id', '')  # Assuming you're sending the user ID too

    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    # Check if the promo code has already been used
    for code in codes:
        if is_code_used(code):
            return jsonify({'error': f'Promo code {code} has already been used'}), 400

    # Write the used codes to used_codes.csv
    write_codes(USED_FILE, codes, user_id)

    # Remove the used codes from promo_codes.csv
    remove_used(codes)

    return jsonify({"status": "success", "used": codes})

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
