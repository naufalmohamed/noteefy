from flask import Flask, render_template, request, redirect, url_for
import psycopg2 
from urllib.parse import urlparse

app = Flask(__name__)

result = urlparse("postgres://qmnyuigfxkvneg:a46f13b306a3a3de3d4e7f373f65a258203661a682b624f49c0e21a79ca863f2@ec2-54-155-254-112.eu-west-1.compute.amazonaws.com:5432/dvv1uhocoo0e9")

username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname
port = result.port

def todo_create_table(username,password,database,hostname,port):
	dbconn = psycopg2.connect(database = database,user = username,password = password,host = hostname,port = port)
	cursor = dbconn.cursor()
	cursor.execute("CREATE TABLE IF NOT EXISTS todo_table( id serial PRIMARY KEY, title VARCHAR(50) NOT NULL,status BOOLEAN NOT NULL);")
	dbconn.commit()
		
	
def select_from_table(username,password,database,hostname,port):
	dbconn = psycopg2.connect(database = database,user = username,password = password,host = hostname,port = port)
	cursor = dbconn.cursor()
	cursor.execute("SELECT * FROM todo_table;")
	todo_list = cursor.fetchall()
	dbconn.commit()
	return todo_list
	
	
@app.route("/")
def index():
	todo_list = select_from_table(username,password,database,hostname,port)
	return render_template("base.html", todo_list = todo_list)
	
	
@app.route("/add", methods=["POST"])
def todo_add_to_table(username,password,database,hostname,port):
	title_ret= request.form.get("title")
	dbconn = psycopg2.connect(database = database,user = username,password = password,host = hostname,port = port)
	cursor = dbconn.cursor()
	cursor.execute("""INSERT INTO todo_table (title, status) VALUES (%s,%s);""",(title_ret, False))
	dbconn.commit()
	return redirect(url_for("index"))
	
	
@app.route("/update/<int:todo_id>")
def todo_update(todo_id,username,password,database,hostname,port):
	dbconn = psycopg2.connect(database = database,user = username,password = password,host = hostname,port = port)
	cursor = dbconn.cursor()
	cursor.execute("""UPDATE todo_table SET status = %s WHERE id = %s;""",(True,todo_id))
	dbconn.commit()
	return redirect(url_for("index"))
	
	
@app.route("/update_not/<int:todo_id>")
def todo_update_not(todo_id):
	dbconn = psycopg2.connect(database = database,user = username,password = password,host = hostname,port = port)
	cursor = dbconn.cursor()
	cursor.execute("""UPDATE todo_table SET status = %s WHERE id = %s;""",(False,todo_id))
	dbconn.commit()
	return redirect(url_for("index"))
	
	
@app.route("/delete/<int:todo_id>")
def todo_delete(todo_id,username,password,database,hostname,port):
	dbconn = psycopg2.connect(database = database,user = username,password = password,host = hostname,port = port)
	cursor = dbconn.cursor()
	cursor.execute("""DELETE from todo_table WHERE id = %s;""",[todo_id])
	dbconn.commit()
	return redirect(url_for("index"))


if __name__ == "__main__":

	todo_create_table(username,password,database,hostname,port)
	app.run(debug=True)
