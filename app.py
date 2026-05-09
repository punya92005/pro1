# app.py

from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================= DATABASE =================

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():

    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS posts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        caption TEXT,
        image TEXT,
        likes INTEGER DEFAULT 0
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS comments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        user TEXT,
        comment TEXT
    )
    """)

    conn.commit()
    conn.close()

create_tables()

# ================= AUTH =================

@app.route('/')
def home():
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = get_db()

        conn.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, password)
        )

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template("register.html")

@app.route('/login', methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']

    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    ).fetchone()

    conn.close()

    if user:
        session['user'] = username
        return redirect('/dashboard')

    return "Invalid Login"

# ================= DASHBOARD =================

@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/')

    conn = get_db()

    posts = conn.execute(
        "SELECT * FROM posts ORDER BY id DESC"
    ).fetchall()

    comments_data = conn.execute(
        "SELECT * FROM comments"
    ).fetchall()

    conn.close()

    comments = {}

    for c in comments_data:
        comments.setdefault(c['post_id'], []).append(c)

    return render_template(
        "dashboard.html",
        posts=posts,
        comments=comments
    )

# ================= CREATE POST =================

@app.route('/create', methods=['GET', 'POST'])
def create():

    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':

        caption = request.form['caption']

        file = request.files['image']

        filename = ""

        if file and file.filename:

            filename = file.filename

            file.save(
                os.path.join(UPLOAD_FOLDER, filename)
            )

        conn = get_db()

        conn.execute(
            "INSERT INTO posts(user,caption,image) VALUES(?,?,?)",
            (session['user'], caption, filename)
        )

        conn.commit()
        conn.close()

        return redirect('/dashboard')

    return render_template("create.html")

# ================= SINGLE POST =================

@app.route('/post/<int:id>')
def single_post(id):

    conn = get_db()

    post = conn.execute(
        "SELECT * FROM posts WHERE id=?",
        (id,)
    ).fetchone()

    comments = conn.execute(
        "SELECT * FROM comments WHERE post_id=?",
        (id,)
    ).fetchall()

    conn.close()

    return render_template(
        "single_post.html",
        post=post,
        comments=comments
    )

# ================= LIKE =================

@app.route('/like/<int:id>')
def like(id):

    conn = get_db()

    conn.execute(
        "UPDATE posts SET likes = likes + 1 WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# ================= DELETE POST =================

@app.route('/delete_post/<int:id>')
def delete_post(id):

    conn = get_db()

    conn.execute(
        "DELETE FROM posts WHERE id=?",
        (id,)
    )

    conn.execute(
        "DELETE FROM comments WHERE post_id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# ================= COMMENT =================

@app.route('/comment/<int:id>', methods=['POST'])
def comment(id):

    text = request.form['comment']

    conn = get_db()

    conn.execute(
        "INSERT INTO comments(post_id,user,comment) VALUES(?,?,?)",
        (id, session['user'], text)
    )

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# ================= LOGOUT =================

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')

# ================= RUN =================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )


    @app.route('/dashboard')
    def dashboard():

        posts = get_posts()

        share_links = {}

        for p in posts:
            share_links[p['id']] = url_for(
                'single_post',
                id=p['id'],
                _external=True
            )

        return render_template(
            "dashboard.html",
            posts=posts,
            share_links=share_links
        )


    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000, debug=True)