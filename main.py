import sqlite3
from sqlite3 import Error
from flask import Flask, request, render_template

app = Flask(__name__)

create_user_table = """
    CREATE TABLE user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name VARCHAR(255),
        middle_name VARCHAR(255),
        second_name VARCHAR(255),
        login VARCHAR(255),
        password VARCHAR(255)
    );
""" 

def get_full_name(first_name, middle_name, second_name):
    return first_name + " " + middle_name + " " + second_name


def get_all_users():
    connection = create_connection('db.sqlite')
    
    select_users = "select * from user"
    users = execute_read_query(connection, select_users)

    return users


def create_connection(path):
    connection = None

    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


def execute_query(connection, query):
    cursor = connection.cursor()

    try:
        cursor.execute(query)

        connection.commit()
        
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None

    try:
        cursor.execute(query)
        result = cursor.fetchall()

        return result
    except Error as e:
        print(f"The error '{e}' occurred")

@app.route('/')
def index():
    return render_template("index.html")
    
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        login = request.form['login']
        password = request.form['password']

        users = get_all_users()

        for user in users:
            id, first, middle, second, l, p = user

            if l == login and p == password:
                return render_template("info.html", first=first, middle=middle, second=second, login=l)

        return render_template("login.html")

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'GET':
        return render_template('reg.html')
    else:
        connection = create_connection('db.sqlite')

        first_name = request.form["firstName"]
        middle_name = request.form["middleName"]
        second_name = request.form["secondName"]
        login = request.form["login"]
        password = request.form["password"]

        values ="'" + first_name + "', '" + middle_name + "', '" + second_name + "', '" + login + "', '" + password + "'"

        query = "INSERT INTO user (first_name, middle_name, second_name, login, password) VALUES (" + values + ")"

        execute_query(connection, query)

        fullname = get_full_name(first_name, middle_name, second_name)

        return render_template('success_reg.html', fullname=fullname)

@app.route('/email', methods=['GET', 'POST'])
def email():
    if request.method == 'GET':
        return render_template('app.html')
    else:
        email = request.form['email']

        return render_template('email.html', email=email)

end_message = " хуйня"

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'GET':
        return render_template('quiz.html')
    else:
        user_answer_1 = request.form["Question1"]
        user_answer_2 = request.form["Question2"]
        user_answer_3 = request.form["Question3"]
        print(user_answer_1,user_answer_2,user_answer_3)

        return render_template('summary.html', end_message="ЖОПА!!!")
    

@app.route('/summary', methods=['GET', 'POST'])
def summary():
    if request.method == 'GET':
        return render_template('summary.html', end_message=end_message)
    else:
        return render_template('quiz.html')



def main():
    # execute_query(connection, create_user_table)

    app.run()


main()