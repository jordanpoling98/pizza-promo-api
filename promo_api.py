@app.route('/promo-codes/mark-used', methods=['POST'])
def mark_promo_codes_used():
    data = request.get_json()
    codes = data.get('codes', [])
    user_email = data.get('user_email')

    if not codes:
        return jsonify({'error': 'No codes provided'}), 400
    if not user_email:
        return jsonify({'error': 'User ID (email) is required'}), 400

    write_codes_to_google(codes, user_email)
    remove_used_from_google(codes)

    return jsonify({'status': 'success', 'used': codes}), 200
