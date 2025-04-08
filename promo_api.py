from flask import Flask, request, jsonify
import os

app = Flask(__name__)
CSV_FILE = 'promo_codes.csv'
USED_FILE = 'used_codes.csv'

# Read codes from a file (removes BOMs + strips lines)
def read_codes(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, 'r', encoding='utf-8-sig') as f:
        return [line.strip() for line in f if line.strip()]

# Write used codes to file
def write_codes(filename, codes):
    try:
        with open(filename, 'a', encoding='utf-8') as f:
            for code in codes:
                f.write(code.strip() + '\n')
    except PermissionError:
        print(f"⚠️ Cannot write to {filename}. File may be open elsewhere.")

# Remove codes that have been used
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

@app.route('/promo-codes', methods=['GET'])
def get_codes():
    count = int(request.args.get('count', 1))
    codes = read_codes(CSV_FILE)

    if not codes:
        return jsonify({"error": "No promo codes available."}), 404

    print(f"📦 Previewing {count} unassigned code(s): {codes[:count]}")
    return jsonify(codes[:count])



@app.route('/promo-codes/mark-used', methods=['POST'])
def mark_used():
    data = request.get_json()
    codes = data.get('codes', [])
    write_codes(USED_FILE, codes)
    remove_used(codes)
    return jsonify({"status": "success", "used": codes})

@app.route('/promo-codes/preview', methods=['GET'])
def preview_codes():
    count = int(request.args.get('count', 1))
    threshold = 10

    codes = read_codes(CSV_FILE)

    if not codes:
        return jsonify({
            "error": "No promo codes available.",
            "action_required": "Please replenish the promo code list."
        }), 404

    preview = codes[:count]

    response = {
        "preview_codes": preview
    }

    if len(preview) < count:
        response["warning"] = f"Only {len(preview)} promo code(s) available. Please replenish the promo code list soon."

    remaining_codes = len(codes) - len(preview)
    if remaining_codes < threshold:
        response["low_inventory_alert"] = f"Only {remaining_codes} promo code(s) left. Please upload more soon."

    return jsonify(response)



if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)


