from flask import Flask, request, jsonify
import sqlite3
import datetime
import os

app = Flask(__name__)

DB_NAME = os.environ.get("DB_PATH", "/tmp/database.db")

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

@app.route('/api/comments', methods=['GET'])
def get_comments():
    try:
        init_db()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT author, text, created_at FROM comments ORDER BY id DESC')
        rows = cursor.fetchall()
        conn.close()
        
        comments = [{"author": r[0], "text": r[1], "date": r[2]} for r in rows]
        return jsonify(comments)
    except Exception as e:
        return jsonify({"error": str(e), "fallback": True}), 200

@app.route('/api/comments', methods=['POST'])
def add_comment():
    try:
        init_db()
        data = request.get_json() or {}
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500
