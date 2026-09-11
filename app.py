from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import datetime
import os

app = Flask(__name__, static_folder='.')
DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            text TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/comments', methods=['GET'])
def get_comments():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT author, text, created_at FROM comments ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    
    comments = [{"author": r[0], "text": r[1], "date": r[2]} for r in rows]
    return jsonify(comments)

@app.route('/api/comments', methods=['POST'])
def add_comment():
    data = request.get_json()
    author = data.get('author')
    text = data.get('text')
    
    if not author or not text:
        return jsonify({"error": "Faltan datos"}), 400
        
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO comments (author, text, created_at) VALUES (?, ?, ?)', (author, text, now))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True}), 201

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)