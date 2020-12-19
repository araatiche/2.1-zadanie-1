import sqlite3
from sqlite3 import Error
from flask import Flask, request, render_template

app = Flask(__name__)

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