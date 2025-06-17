from flask import Flask, request, jsonify, render_template
import datetime
import os

app = Flask(__name__, static_folder='static', template_folder='templates')

# In-memory data store for simplicity
# In a real application, you would use a database.
gratitudes = []

@app.route('/')
def index():
    return render_template('entry.html', active_page='entry')

@app.route('/gratitudes', methods=['GET'])
def get_gratitudes():
    return jsonify(sorted(gratitudes, key=lambda x: x['timestamp'], reverse=True))

@app.route('/gratitudes', methods=['POST'])
def add_gratitude():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing text'}), 400

    new_gratitude = {
        'id': len(gratitudes) + 1,
        'text': data['text'],
        'timestamp': datetime.datetime.utcnow().isoformat() + 'Z' # ISO 8601 format
    }
    gratitudes.append(new_gratitude)
    return jsonify(new_gratitude), 201

@app.route('/calendar')
def calendar():
    return render_template('calendar.html', active_page='calendar')

@app.route('/gratitude/<date>')
def gratitude_for_day(date):
    # date is in YYYY-MM-DD format
    entries = [g for g in gratitudes if g['timestamp'].startswith(date)]
    return render_template('gratitude_day.html', date=date, entries=entries)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
