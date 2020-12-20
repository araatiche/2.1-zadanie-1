import sqlite3
import copy
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
# запрос для создания таблицы ответов, запись в ней состоит из: уникальный ключ, id текущего пользователя сдававшего тест, вопрос, ответ
create_qa_table = """
    CREATE TABLE user_qa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INT,
        question VARCHAR(255),
        user_answer VARCHAR(255)
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

# стартовая страница, можно войти, можно попасть либо войти в систему под уже существующими данными, либо попасть на страницу регистрации

current_user_id = "" # глобальная переменная чтобы хранить id текущего пользователя после входа

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("index.html")
    else:
        login = request.form['login']
        password = request.form['password']

        users = get_all_users()

        for user in users:
            id, first, middle, second, l, p = user

            if l == login and p == password:
                global current_user_id # внутри функции говорим что переменная глобальная, чтобы записать в нее результат и использовать его в другой функции
                current_user_id = copy.deepcopy(user[0])
                print("id текущего пользоватля:", current_user_id)
                return render_template("user_menu.html", first=first, middle=middle)
                 
        return render_template("index.html", incorect_login_message = "Неверное имя пользователя или пароль!") # если введенные данные не соответвуют каким либо из базы выводим сообщение

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

# лист вопросов и правильных ответов на них
qa_list = [
    ("Сколько пальцев на руке?", "5"),
    ("Вы человек?", "да"),
    ("Изучаемый в курсе язык програмирования?", "python"),
]

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'GET':
        return render_template('quiz.html', Question1 = qa_list[0][0], Question2 = qa_list[1][0], Question3 = qa_list[2][0]) # при вызове страницы заполняем шаблон вопросами из листа вопросов
    else:
        # когда происходит отправка ответов на сервер считываем ответы из формы
        user_answer_1 = request.form["Answer1"]
        user_answer_2 = request.form["Answer2"]
        user_answer_3 = request.form["Answer3"]
        right_answer_count = 0 # объявляем счетчик правильных ответов
        if user_answer_1.strip().lower() == qa_list[0][1]: # в случае если ответ данный пользователем равен ответу из листа, увеличиваем значение правильных ответов
            right_answer_count += 1
        if user_answer_2.strip().lower() == qa_list[1][1]:
            right_answer_count += 1
        if user_answer_3.strip().lower() == qa_list[2][1]:
            right_answer_count += 1
        if right_answer_count == 3:
            end_message = "Молодец! Так держать." # формируем сообщение для пользователя в зависимости от количества правильных ответов
        else:
            end_message =  "Попробуйте еще раз, у вас полчится!"

        # записываем данные в базу данных
        print("id текущего пользоватля:", current_user_id)

        connection = create_connection('db.sqlite')
    
        values = "'" + str(current_user_id) + "', '" + qa_list[0][0] + "', '" + user_answer_1 + "'"
        query = "INSERT INTO user_qa (user_id, question, user_answer) VALUES (" + values + ")"
        execute_query(connection, query)

        values = "'" + str(current_user_id) + "', '" + qa_list[1][0] + "', '" + user_answer_2 + "'"
        query = "INSERT INTO user_qa (user_id, question, user_answer) VALUES (" + values + ")"
        execute_query(connection, query)

        values = "'" + str(current_user_id) + "', '" + qa_list[2][0] + "', '" + user_answer_3 + "'"
        query = "INSERT INTO user_qa (user_id, question, user_answer) VALUES (" + values + ")"
        execute_query(connection, query)

        return render_template('summary.html', right_answer_count = right_answer_count, total_answer_count = len(qa_list), end_message=end_message)
    

@app.route('/all_results')
def all_results():
    # когда пользователь нажимает на кнопку "Просмотреть результаты" создается запрос к БД в котором выгружаются его предыдущие попытки ответов 
    # данные по конкретному пользователю выдаются за счет использования переменной current_user_id
    connection = create_connection('db.sqlite')
    select_qa = "SELECT user.second_name, user.first_name, user.middle_name, user_qa.question, user_qa.user_answer FROM user JOIN user_qa ON user.id = user_qa.user_id WHERE user_qa.user_id ="+ str(current_user_id)+""
    print(select_qa)
    rows = execute_read_query(connection, select_qa)

    return render_template('all_results.html', rows = rows) # и выводятся на страницу в виде таблицы





def main():
    # execute_query(connection, create_user_table)

    #connection = create_connection('db.sqlite')
    #execute_query(connection, create_qa_table)
    app.run()


main()