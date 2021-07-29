from flask import Flask, render_template, request, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
import os
import psycopg2 
from urllib.parse import urlparse
import datetime
from psycopg2 import sql
import function


from auth_decorator import login_required

app = Flask(__name__)
app.secret_key = "APP_SECRET_KEY"
app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=5)


oauth = OAuth(app)
google = oauth.register(
    name='google', 
    client_id="538430542715-7kth3mlrhg9p72e9pqoqinnr80424crp.apps.googleusercontent.com",
    client_secret="ICRfDwSndb0Hgf6mf2gdLXsg",
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo', 
    client_kwargs={'scope': 'openid email profile'},
)


def parse():
	result = urlparse("postgres://kbavvbvdsgyxem:b87e8fa4e189c9d220d887fe487e0d0bd0a01e8af76dab2e0e2820766a91d1d4@ec2-52-1-20-236.compute-1.amazonaws.com:5432/d7dv0rn1807k9k")
	username = result.username
	password = result.password
	database = result.path[1:]
	hostname = result.hostname
	port = result.port
	return username, password, database, hostname, port

		
@app.route('/login')
def login():
    google = oauth.create_client('google')  
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')  
    token = google.authorize_access_token() 
    resp = google.get('userinfo')  
    user_info = resp.json()
    user = oauth.google.userinfo()  
    session['profile'] = user_info
    session.permanent = True  
    return redirect('/profile')


@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')
	
	
@app.route('/')
def index():
	return render_template("index.html")
	
	
@app.route('/profile')
@login_required
def profile():
	name_info = dict(session)['profile']['name']
	email = dict(session)['profile']['email']
	pic_info =  dict(session)['profile']['picture']
	email_ret = email.split("@")
	#print(email)
	#email = dict(session)['profile']['email']
	username, password, database, hostname, port = parse()
	dbconn = psycopg2.connect(database = database,user = username,password = password,host = hostname,port = port)
	cursor = dbconn.cursor()
	cursor.execute(f"CREATE TABLE IF NOT EXISTS {email_ret[0]} ( id serial PRIMARY KEY, title VARCHAR(50) NOT NULL,date VARCHAR, tags VARCHAR [], description VARCHAR);")
	cursor.execute(f"SELECT * FROM {email_ret[0]};")
	todo_list = cursor.fetchall()
	dbconn.commit()
	return render_template("profile.html", todo_list = todo_list, email=email, pic_info=pic_info,name_info=name_info)
	
@app.route("/add_new")
def add_new():
	return render_template("note.html")
	
	
@app.route("/add", methods=["POST"])
def todo_add_to_table():
	email = dict(session)['profile']['email']
	email_ret = email.split("@")
	username, password, database, hostname, port = parse()
	title_ret= request.form.get("title")
	tags_ret= request.form.get("tags")
	tags = tags_ret.split(",")
	description_ret= request.form.get("description")
	date = datetime.date.today()
	
	if len(title_ret) == 0 and len(description_ret) == 0:
			return redirect(url_for("profile"))
			
	else:		
		dbconn = psycopg2.connect(database = database,user = username,password = password,host = hostname,port = port)
		cursor = dbconn.cursor()
		cursor.execute(f"""INSERT INTO {email_ret[0]} (title, date, tags, description) VALUES (%s,%s,%s,%s);""",(title_ret,date,tags,description_ret))
		dbconn.commit()
		return redirect(url_for("profile"))
	
	
@app.route("/search", methods=["POST"])
def todo_search_tags():
	name_info = dict(session)['profile']['name']
	pic_info =  dict(session)['profile']['picture']
	email = dict(session)['profile']['email']
	email_ret = email.split("@")
	tag_ret= request.form.get("search")
	title_ret= request.form.get("title")
	username, password, database, hostname, port = parse()
	dbconn = psycopg2.connect(database = database,user = username,password = password,host = hostname,port = port)
	cursor = dbconn.cursor()
	cursor.execute(f"SELECT * FROM {email_ret[0]};")
	todo_list = cursor.fetchall()
	dbconn.commit()
	tag_list = []
	for todo in todo_list:
		for tag in todo[3]:
			if tag == tag_ret:
				tag_list.append(todo)
	
	return render_template("search.html", tag_list = tag_list,email=email,pic_info=pic_info,name_info=name_info)
		
	
@app.route("/search_tags/<tag>")
def todo_search_tags_hash(tag):
	email = dict(session)['profile']['email']
	email_ret = email.split("@")
	tag_ret= request.form.get("search")
	title_ret= request.form.get("title")
	username, password, database, hostname, port = parse()
	dbconn = psycopg2.connect(database = database,user = username,password = password,host = hostname,port = port)
	cursor = dbconn.cursor()
	cursor.execute(f"SELECT * FROM {email_ret[0]};")
	todo_list = cursor.fetchall()
	dbconn.commit()
	tag_list = []

	
	for todo in todo_list:
		for tagg in todo[3]:
			if tagg == tag:
				tag_list.append(todo)
	
	return render_template("search.html", tag_list = tag_list)	
	
	
@app.route("/update/<int:todo_id>")
@login_required
def todo_update(todo_id):
	email = dict(session)['profile']['email']
	email_ret = email.split("@")
	tag_ret= request.form.get("search")
	title_ret= request.form.get("title")
	username, password, database, hostname, port = parse()
	dbconn = psycopg2.connect(database = database,user = username,password = password,host = hostname,port = port)
	cursor = dbconn.cursor()
	cursor.execute(f"SELECT * FROM {email_ret[0]};")
	todo_list = cursor.fetchall()
	dbconn.commit()
	for todo in todo_list:
		if todo[0] == todo_id:
			row = todo
	
	return render_template("update.html", row = row)
	
	
@app.route("/update_old/<int:row_id>", methods = ["POST"])
@login_required
def todo_update_old(row_id):
	email = dict(session)['profile']['email']
	email_ret = email.split("@")
	todo_id = row_id
	title_ret= request.form.get("title")
	tags_ret= request.form.get("tags")
	tags = tags_ret.split(",")
	description_ret= request.form.get("description")
	date = datetime.date.today()
	username, password, database, hostname, port = parse()
	dbconn = psycopg2.connect(database = database,user = username,password = password,host = hostname,port = port)
	cursor = dbconn.cursor()
	cursor.execute(f"""UPDATE {email_ret[0]} SET title = %s WHERE id = %s;""",(title_ret,todo_id))
	cursor.execute(f"""UPDATE {email_ret[0]} SET description = %s WHERE id = %s;""",(description_ret,todo_id))
	cursor.execute(f"""UPDATE {email_ret[0]} SET tags = %s WHERE id = %s;""",(tags,todo_id))
	dbconn.commit()
	return redirect(url_for("profile"))
	
	
@app.route("/delete/<int:todo_id>")
def todo_delete(todo_id):
	email = dict(session)['profile']['email']
	email_ret = email.split("@")
	username, password, database, hostname, port = parse()
	dbconn = psycopg2.connect(database = database,user = username,password = password,host = hostname,port = port)
	cursor = dbconn.cursor()
	cursor.execute(f"""DELETE from {email_ret[0]} WHERE id = %s;""",[todo_id])
	dbconn.commit()
	return redirect(url_for("profile"))


if __name__ == "__main__":
	#todo_drop_table()
	#todo_create_table()
	app.run(debug=True)
