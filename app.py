from flask import Flask, render_template, request, redirect, url_for
import psycopg2 
from urllib.parse import urlparse
import datetime

app = Flask(__name__)


def parse():
	result = urlparse("postgres://qmnyuigfxkvneg:a46f13b306a3a3de3d4e7f373f65a258203661a682b624f49c0e21a79ca863f2@ec2-54-155-254-112.eu-west-1.compute.amazonaws.com:5432/dvv1uhocoo0e9")
	username = result.username
	password = result.password
	database = result.path[1:]
	hostname = result.hostname
	port = result.port
	return username, password, database, hostname, port

def todo_create_table():
	username, password, database, hostname, port = parse()
	dbconn = psycopg2.connect(database = database,user = username,password = password,host = hostname,port = port)
	cursor = dbconn.cursor()
	cursor.execute("CREATE TABLE IF NOT EXISTS todo_table( id serial PRIMARY KEY, title VARCHAR(50) NOT NULL,date VARCHAR, tags VARCHAR [], description VARCHAR);")
	dbconn.commit()
	
	
def todo_drop_table():
	username, password, database, hostname, port = parse()
	dbconn = psycopg2.connect(database = database,user = username,password = password,host = hostname,port = port)
	cursor = dbconn.cursor()
	cursor.execute("DROP TABLE todo_table;")
	dbconn.commit()
		
	
def select_from_table():
	title_ret= request.form.get("title")
	username, password, database, hostname, port = parse()
	dbconn = psycopg2.connect(database = database,user = username,password = password,host = hostname,port = port)
	cursor = dbconn.cursor()
	cursor.execute("SELECT * FROM todo_table;")
	todo_list = cursor.fetchall()
	dbconn.commit()
	return todo_list
	
	
@app.route("/")
def index():
	todo_list = select_from_table()
	return render_template("index.html", todo_list = todo_list)
	
@app.route("/add_new")
def add_new():
	return render_template("note.html")
	
	
@app.route("/add", methods=["POST"])
def todo_add_to_table():
	username, password, database, hostname, port = parse()
	title_ret= request.form.get("title")
	tags_ret= request.form.get("tags")
	tags = tags_ret.split(",")
	description_ret= request.form.get("description")
	date = datetime.date.today()
	
	if len(title_ret) == 0 and len(description_ret) == 0:
			return redirect(url_for("index"))
			
	else:		
		dbconn = psycopg2.connect(database = database,user = username,password = password,host = hostname,port = port)
		cursor = dbconn.cursor()
		cursor.execute("""INSERT INTO todo_table (title, date, tags, description) VALUES (%s,%s,%s,%s);""",(title_ret,date,tags,description_ret))
		dbconn.commit()
		return redirect(url_for("index"))
	
	
@app.route("/search", methods=["POST"])
def todo_search_tags():
	tag_ret= request.form.get("search")
	todo_list = select_from_table()
	tag_list = []
	for todo in todo_list:
		for tag in todo[3]:
			if tag == tag_ret:
				tag_list.append(todo)
	
	return render_template("search.html", tag_list = tag_list)
		
	
@app.route("/search_tags/<tag>")
def todo_search_tags_hash(tag):
	todo_list = select_from_table()
	tag_list = []

	
	for todo in todo_list:
		for tagg in todo[3]:
			if tagg == tag:
				tag_list.append(todo)
	
	return render_template("search.html", tag_list = tag_list)	
	
	
@app.route("/update/<int:todo_id>")
def todo_update(todo_id):
	todo_list = select_from_table()
	for todo in todo_list:
		if todo[0] == todo_id:
			row = todo
	
	return render_template("update.html", row = row)
	
	
@app.route("/update_old/<int:row_id>", methods = ["POST"])
def todo_update_old(row_id):
	todo_id = row_id
	title_ret= request.form.get("title")
	tags_ret= request.form.get("tags")
	tags = tags_ret.split(",")
	description_ret= request.form.get("description")
	date = datetime.date.today()
	username, password, database, hostname, port = parse()
	dbconn = psycopg2.connect(database = database,user = username,password = password,host = hostname,port = port)
	cursor = dbconn.cursor()
	cursor.execute("""UPDATE todo_table SET title = %s WHERE id = %s;""",(title_ret,todo_id))
	cursor.execute("""UPDATE todo_table SET description = %s WHERE id = %s;""",(description_ret,todo_id))
	cursor.execute("""UPDATE todo_table SET tags = %s WHERE id = %s;""",(tags,todo_id))
	cursor.execute("""UPDATE todo_table SET date = %s WHERE id = %s;""",(date,todo_id))
	dbconn.commit()
	return redirect(url_for("index"))
	
	
@app.route("/delete/<int:todo_id>")
def todo_delete(todo_id):
	username, password, database, hostname, port = parse()
	dbconn = psycopg2.connect(database = database,user = username,password = password,host = hostname,port = port)
	cursor = dbconn.cursor()
	cursor.execute("""DELETE from todo_table WHERE id = %s;""",[todo_id])
	dbconn.commit()
	return redirect(url_for("index"))


if __name__ == "__main__":
	#todo_drop_table()
	todo_create_table()
	app.run(debug=True)
