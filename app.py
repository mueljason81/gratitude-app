from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import datetime
import os

app = Flask(__name__, static_folder='static', template_folder='templates')

# Configure SQLAlchemy with PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Gratitude(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.String(32), nullable=False)  # ISO8601 string

@app.route('/')
def index():
    return render_template('entry.html', active_page='entry')

@app.route('/gratitudes', methods=['GET'])
def get_gratitudes():
    gratitudes = Gratitude.query.order_by(Gratitude.timestamp.desc()).all()
    return jsonify([
        {'id': g.id, 'text': g.text, 'timestamp': g.timestamp}
        for g in gratitudes
    ])

@app.route('/gratitudes', methods=['POST'])
def add_gratitude():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing text'}), 400
    timestamp = datetime.datetime.utcnow().isoformat() + 'Z'
    g = Gratitude(text=data['text'], timestamp=timestamp)
    db.session.add(g)
    db.session.commit()
    return jsonify({'id': g.id, 'text': g.text, 'timestamp': g.timestamp}), 201

@app.route('/calendar')
def calendar():
    return render_template('calendar.html', active_page='calendar')

from dateutil import parser
import pytz

@app.route('/gratitude/<date>')
def gratitude_for_day(date):
    # date is in YYYY-MM-DD format
    tz = pytz.timezone('US/Pacific')
    entries = Gratitude.query.all()
    matching = []
    for g in entries:
        utc_dt = parser.isoparse(g.timestamp)
        local_dt = utc_dt.astimezone(tz)
        if local_dt.strftime('%Y-%m-%d') == date:
            matching.append(g)
    return render_template('gratitude_day.html', date=date, entries=matching)

@app.route('/initdb')
def initdb():
    db.create_all()
    return 'Database initialized!'

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
