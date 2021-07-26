from flask import Flask, render_template, request, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
import os
import psycopg2 
from urllib.parse import urlparse
import datetime
import function


def parse():
	result = urlparse("postgres://kbavvbvdsgyxem:b87e8fa4e189c9d220d887fe487e0d0bd0a01e8af76dab2e0e2820766a91d1d4@ec2-52-1-20-236.compute-1.amazonaws.com:5432/d7dv0rn1807k9k")
	username = result.username
	password = result.password
	database = result.path[1:]
	hostname = result.hostname
	port = result.port
	return username, password, database, hostname, port

def todo_create_table(email):
	#email = dict(session)['profile']['email']
	username, password, database, hostname, port = parse()
	dbconn = psycopg2.connect(database = database,user = username,password = password,host = hostname,port = port)
	cursor = dbconn.cursor()
	cursor.execute("CREATE TABLE IF NOT EXISTS %s ( id serial PRIMARY KEY, title VARCHAR(50) NOT NULL,date VARCHAR, tags VARCHAR [], description VARCHAR);",(email))
	dbconn.commit()

	
	
def todo_drop_table():
	username, password, database, hostname, port = parse()
	dbconn = psycopg2.connect(database = database,user = username,password = password,host = hostname,port = port)
	cursor = dbconn.cursor()
	cursor.execute("DROP TABLE todo_table;")
	dbconn.commit()
		
	
def select_from_table():
	#email = dict(session)['profile']['email']
	title_ret= request.form.get("title")
	username, password, database, hostname, port = parse()
	dbconn = psycopg2.connect(database = database,user = username,password = password,host = hostname,port = port)
	cursor = dbconn.cursor()
	cursor.execute("SELECT * FROM todo_table;")
	todo_list = cursor.fetchall()
	dbconn.commit()
	return todo_list

