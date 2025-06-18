from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import datetime
import os
from threading import Thread
from dotenv import load_dotenv
load_dotenv()
import openai

app = Flask(__name__, static_folder='static', template_folder='templates')

# Database configuration: use DATABASE_URL if set, otherwise fallback to SQLite for local dev
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///gratitude.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Gratitude(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.String(32), nullable=False)  # ISO8601 string
    image_url = db.Column(db.Text, nullable=True)  # Stores OpenAI image URL

@app.route('/')
def index():
    return render_template('entry.html', active_page='entry')

@app.route('/gratitudes', methods=['GET'])
def get_gratitudes():
    gratitudes = Gratitude.query.order_by(Gratitude.timestamp.desc()).all()
    return jsonify([
        {'id': g.id, 'text': g.text, 'timestamp': g.timestamp, 'image_url': g.image_url} for g in gratitudes
    ])

@app.route('/gratitudes', methods=['POST'])
def add_gratitude():
    data = request.get_json()
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'Text is required'}), 400
    timestamp = datetime.datetime.now(pytz.utc).isoformat()
    gratitude = Gratitude(text=text, timestamp=timestamp, image_url=None)
    db.session.add(gratitude)
    db.session.commit()

    def generate_and_update_image(gratitude_id, text):
        # Create a new app context for the thread
        with app.app_context():
            try:
                openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
                response = openai_client.images.generate(
                    model="dall-e-3",
                    prompt=text,
                    n=1,
                    size="1024x1024"
                )
                image_url = response.data[0].url
                g = Gratitude.query.get(gratitude_id)
                if g:
                    g.image_url = image_url
                    db.session.commit()
            except Exception as e:
                print(f"OpenAI image generation failed: {e}")
    Thread(target=generate_and_update_image, args=(gratitude.id, text)).start()

    return jsonify({'id': gratitude.id, 'text': gratitude.text, 'timestamp': gratitude.timestamp, 'image_url': gratitude.image_url}), 201

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
    # Format hero string: "Wednesday, June 18th 2025 was awesome because ..."
    import calendar
    import datetime
    def ordinal(n):
        if 10 <= n % 100 <= 20:
            return str(n) + 'th'
        else:
            return str(n) + {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    try:
        dt = datetime.datetime.strptime(date, '%Y-%m-%d')
        weekday = dt.strftime('%A')
        month = dt.strftime('%B')
        day = ordinal(dt.day)
        year = dt.year
        gratitudes = [g.text for g in matching]
        if gratitudes:
            joined = ' and '.join(gratitudes)
            hero = f"{weekday}, {month} {day} {year} was awesome because I am grateful for {joined}!"
        else:
            hero = f"{weekday}, {month} {day} {year} was awesome!"
    except Exception as e:
        hero = date
    return render_template('gratitude_day.html', date=date, entries=matching, hero=hero)


@app.route('/initdb')
def initdb():
    db.create_all()
    return 'Database initialized!'

if __name__ == '__main__':
    import sys
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port: {sys.argv[1]}, using default 5000")
    app.run(debug=True, host='0.0.0.0', port=port)
