import flask
from flask import jsonify
from flask import request
import mysql.connector
from mysql.connector import Error
from random import randrange

def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host = host_name,
            user = user_name,
            password = user_password,
            database = db_name
        )
        print('Connection to MySQL DB successful.')
    except Error as e:
        print('Failure. The error {} occured.'.format(e))

    return connection
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print('Query executed successfully')
    except Error as e:
        print('The error {} occurred'.format(e))
def execute_read_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print("The error '{}' occurred".format(e))

host = "Your host Name"
user = "Your username"
password = "Your PW"
database = "Your database name"
connection = create_connection(host, user, password, database)

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/api/friends', methods=['POST','PUT','GET'])
def create_modify_friends():

    # Creates a friend
    # When a friend record is created, a trigger is activated which automatically creates a record in the movielist table with its corresponding friendid (movie columns are null)

    if request.method == 'POST':
        request_data = request.get_json()
        query = f"INSERT INTO friend (firstname, lastname) VALUES ('{request_data['firstname']}','{request_data['lastname']}')"
        execute_query(connection, query)
        return 'POST REQUEST adding friend to friend table complete'

    # Updates a friend in the friend table

    if request.method == 'PUT':
        request_data = request.get_json()
        query = f"UPDATE friend SET firstname = '{request_data['firstname']}', lastname = '{request_data['lastname']}' WHERE id = '{request_data['id']}'"
        execute_query(connection,query)
        return 'PUT REQUEST modifying friend table complete'

    # Shows current friends stored in the friend table

    if request.method == 'GET':
        conn = create_connection(host, user, password, database)
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM friend"
        cursor.execute(sql)
        rows = cursor.fetchall()

        results = []
        for user in rows:
            results.append(user)

        return jsonify(results)


@app.route('/api/movies', methods=['POST', 'PUT','GET'])
def choose_friend_movies():

    # The record for the friend in the movielist table has automatically been created by the database when the corresponding record in the friend table was created
    # Modify movie list for a friend
    # The following 2 for loops allow for a query string with changing number of variables

    if request.method == 'PUT':
        request_data = request.get_json()
        list = []
        x = ''
        y = request_data['friendid']
        for key_value_pair in request_data:
            list.append(key_value_pair)
        for i in range(0,len(list)):
            if i < len(list)-1 and list[i] != 'friendid':
                x = x + str(list[i]) + f" = '{request_data[list[i]]}', "
            elif i == len(list)-1 and list[i] != 'friendid':
                x = x + str(list[i]) + f" = '{request_data[list[i]]}' "

        query = f"UPDATE movielist SET {x} WHERE friendid = '{y}'"
        execute_query(connection,query)
        return 'PUT REQUEST modifying movielist table complete'


    # Show movie lists for all friends

    if request.method == 'GET':
        conn = create_connection(host, user, password, database)
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM movielist"
        cursor.execute(sql)
        rows = cursor.fetchall()

        results = []
        for user in rows:
            results.append(user)

        return jsonify(results)


@app.route('/api/generate', methods=['GET'])
def generate_list():

    # This allows a string of ids (in the format of /api/generate?id=1,2,3.....)
    # The string is parsed and the ids are used to create a pool of movies for the friends with those ids
    # The function generate_list then returns a randomly selected movie from that pool of movies

    if 'id' in request.args:
        for arg in request.args:
            print(request.args[arg])
        ids = request.args['id']
        id_list = ids.split(',')
    else:
        return "ERROR: no id provided"

    query = "SELECT friendid,firstname,lastname,movie1,movie2,movie3,movie4,movie5,movie6,movie7,movie8,movie9,movie10 FROM friend INNER JOIN movielist ON friend.id=movielist.friendid"
    rows = execute_read_query(connection,query)
    movies = []
    for row in rows:
        if str(row[0]) in id_list:
            for i in range(3,len(row)):
                if row[i] != None:
                    movies.append(row[i])
    movie = str(movies[randrange(0,len(movies))])

    return f'Randomly generated movie for selected friends is {movie}'


app.run()