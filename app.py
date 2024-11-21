from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
import os
from urllib.parse import urlparse
import datetime
import hashlib
import os
from configparser import ConfigParser


app = Flask(__name__)
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SESSION_COOKIE_NAME'] = 'login-session'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=5)

config = ConfigParser()
config.read('config.cfg')
app.config['SECRET_KEY'] = config['flask']['SECRET_KEY']

def hash_password(password):
    salt = os.urandom(16)
    return salt + hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)

def verify_password(stored_password, provided_password):
    salt = stored_password[:16]
    stored_key = stored_password[16:]
    provided_key = hashlib.pbkdf2_hmac('sha256', provided_password.encode(), salt, 100000)
    return bytes(stored_key) == provided_key

def parse():
    result = urlparse(config['flask']['DB_URL'])
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port
    return username, password, database, hostname, port

def get_db_connection():
    username, password, database, hostname, port = parse()
    return psycopg2.connect(database=database, user=username, password=password, host=hostname, port=port)

def execute_query(query, params=()):
    with get_db_connection() as dbconn:
        with dbconn.cursor() as cursor:
            cursor.execute(query, params)
            dbconn.commit()
            return cursor.fetchall() if query.strip().upper().startswith("SELECT") else None

@app.route('/')
def index():
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = hash_password(request.form['password'])
        try:
            execute_query(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, password)
            )
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except psycopg2.IntegrityError:
            flash('Username or email already exists.', 'danger')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            user = execute_query(
                "SELECT id, password FROM users WHERE email = %s",
                (email,)
            )
            if user and verify_password(user[0][1], password):
                session['user_id'] = user[0][0]
                session.permanent = True
                return redirect(url_for('profile'))
            else:
                flash('Invalid username or password.', 'danger')
        except Exception as e:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = execute_query(
        "SELECT username, email FROM users WHERE id = %s",
        (user_id,)
    )[0]
    todo_list = execute_query(
        "SELECT * FROM todos WHERE user_id = %s",
        (user_id,)
    )
    return render_template('profile.html', user=user, todo_list=todo_list)

@app.route('/add_new')
def add_new():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("note.html")

@app.route("/add", methods=["POST"])
def todo_add_to_table():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    title_ret= request.form.get("title")
    tags_ret= request.form.get("tags")
    tags = tags_ret.split(",")
    description_ret= request.form.get("description")
    date = datetime.date.today()

    if len(title_ret) == 0 and len(description_ret) == 0:
        return redirect(url_for("profile"))
    else:
        execute_query(
            "INSERT INTO todos (user_id, title, date, tags, description) VALUES (%s, %s, %s, %s, %s)",
            (session['user_id'], title_ret, date, tags, description_ret)
        )
        return redirect(url_for("profile"))

@app.route("/search_tags/<tag>")
def todo_search_tags_hash(tag):
    return todo_search_tags(tag_ret=tag, from_click=True)

@app.route("/search", methods=["POST"])
def todo_search_tags(tag_ret=None, from_click=False):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if not from_click:
        tag_ret = request.form.get("search")
    
    # Ensure a tag is provided
    if not tag_ret:
        return redirect(url_for('index'))  
    user_id = session['user_id']
    user = execute_query(
        "SELECT username, email FROM users WHERE id = %s",
        (user_id,)
    )[0]
    todo_list = execute_query(
        "SELECT title, date, tags, description FROM todos WHERE user_id = %s",
        (session['user_id'],)
    )
    tag_list = [todo for todo in todo_list if tag_ret in todo[2]]

    return render_template("search.html", tag_list=tag_list, user=user)


@app.route("/update/<int:todo_id>")
def todo_update(todo_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    todo_list = execute_query(
        "SELECT id, title, date, tags, description FROM todos WHERE id = %s AND user_id = %s",
        (todo_id, session['user_id'])
    )
    row = todo_list[0] if todo_list else None
    
    return render_template("update.html", row=row)

@app.route("/update_old/<int:row_id>", methods = ["POST"])
def todo_update_old(row_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    title_ret = request.form.get("title")
    tags_ret = request.form.get("tags")
    tags = tags_ret.split(",")
    description_ret = request.form.get("description")

    execute_query(
        "UPDATE todos SET title = %s, description = %s, tags = %s WHERE id = %s AND user_id = %s",
        (title_ret, description_ret, tags, row_id, session['user_id'])
    )
    return redirect(url_for("profile"))

@app.route("/delete/<int:todo_id>")
def todo_delete(todo_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    execute_query(
        "DELETE FROM todos WHERE id = %s AND user_id = %s",
        (todo_id, session['user_id'])
    )
    return redirect(url_for("profile"))

if __name__ == "__main__":
    app.run(debug=True)
