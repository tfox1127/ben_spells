import os, random
from typing_extensions import Self
import datetime as dt
from flask import Flask, render_template, request, jsonify, session
from werkzeug.exceptions import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker

DATABASE_URL = os.environ['DATABASE_URL']

app = Flask(__name__)
engine = create_engine(DATABASE_URL, isolation_level="AUTOCOMMIT")
db = scoped_session(sessionmaker(bind=engine))

# app.secret_key = 'your_secret_key'  # Replace with a secure secret key
app.secret_key = os.environ['pizza']

# Sample list of words for practice
#week01 words = ["can't", "don't", "wasn't", "doesn't", "didn't", "what's", "that's", "here's", "he's", "who's"]
words = ["beach", "coast", "neat", "booth", "goat", "sheep", "tail", "wait", "scoop", "wheel"]

@app.route('/')
def home():
    session['user_id'] = random.randint(1000, 9999)
    session['practiced_words'] = []
    session['current_word'] = None
    session['answers'] = []
    return render_template('index.html')

@app.route('/practice', methods=['GET', 'POST'])
def practice():
    if request.method == 'POST':
        user_word = request.form['word']
        original_word = request.form['original_word']
        original_word_original = original_word

        db.execute(text(
            f"""
                INSERT INTO ben_spells_logs (user_id, original_word_original, user_word, original_word, ts)
                VALUES ({session['user_id']}, '{original_word_original}', '{user_word}', '{original_word}', '{dt.datetime.now()}');
            """))
        db.commit()

        user_word = user_word.strip()
        user_word = user_word.replace('’', "'")
        user_word = user_word.replace('‘', "'")
        user_word = user_word.replace('“', '"')
        user_word = user_word.replace('”', '"') 
        user_word = user_word.upper()

        original_word = original_word.strip()
        original_word = original_word.replace('’', "'")
        original_word = original_word.replace('‘', "'")
        original_word = original_word.replace('“', '"')
        original_word = original_word.replace('”', '"') 
        original_word = original_word.upper()

        result = user_word == original_word
        
        if result:
            # Add the word to the list of practiced words
            practiced_words = session.get('practiced_words', [])
            if original_word_original not in practiced_words:
                practiced_words.append(original_word_original)
            session['practiced_words'] = practiced_words

            #pic a random image from the /static/images/happy folder
            happy_images = os.listdir(os.path.join(app.static_folder, 'images/happy'))
            random_happy_image = random.choice(happy_images)

            # Check if all words have been practiced
            if len(practiced_words) == len(words):
                return jsonify(result=result, image=random_happy_image, done=True)
            else:
                session['current_word'] = None
                return jsonify(result=result, image=random_happy_image, done=False)
        else:
            # Pick a random image from the /static/images/sad folder
            sad_images = os.listdir(os.path.join(app.static_folder, 'images/sad'))
            random_sad_image = random.choice(sad_images)
            return jsonify(result=result, done=False, image=random_sad_image)
    else:
        practiced_words = session.get('practiced_words', [])
        current_word = session.get('current_word')

        if not current_word:
            remaining_words = [word for word in words if word not in practiced_words]
            current_word = random.choice(remaining_words)
            session['current_word'] = current_word

        return render_template('practice.html', word=current_word)

@app.route('/reset')
def reset():
    session['practiced_words'] = []
    session['current_word'] = None
    session['answers'] = []
    session['user_id'] = random.randint(1000, 9999)
    
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)