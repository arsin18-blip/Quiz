from flask import Flask, session, redirect, url_for, request, render_template
from db_scripts import get_question_after, get_quises, check_answer
import os
from random import shuffle

folder = os.getcwd()

def start_quiz(quiz_id):
    session['quiz'] = quiz_id
    session['last_question'] = 0
    session['answer'] = 0
    session['total'] = 0

def end_quiz():
    session.clear()

def quiz_form():
    q_list = get_quises()
    return render_template('start.html', q_list=q_list)

def index():
    if request.method == 'GET':
        start_quiz(-1)
        return quiz_form()
    if request.method == 'POST':
        quest_id = request.form.get('quiz')
        start_quiz(int(quest_id))
        return redirect(url_for('test'))

def question_form(question_data):
    answer_list = [question_data[2], question_data[3], question_data[4], question_data[5]]
    shuffle(answer_list)
    return render_template('test.html', 
                          question=question_data[1], 
                          quest_id=question_data[0], 
                          answers_list=answer_list)

def test():
    if not ('quiz' in session) or int(session['quiz']) < 0:
        return redirect(url_for('index'))
    else:
        result = get_question_after(session['last_question'], session['quiz'])
        if result is None or len(result) == 0:
            return redirect(url_for('result'))
        else:
            return question_form(result)

def save_answers():
    answer = request.form.get('ans_text')
    quest_id = request.form.get('q_id')
    session['last_question'] = int(quest_id)
    session['total'] += 1
    if check_answer(int(quest_id), answer):
        session['answer'] += 1
    return redirect(url_for('test'))

def result():
    right = session.get('answer', 0)
    total = session.get('total', 0)
    end_quiz()
    return render_template('result.html', right=right, total=total)

app = Flask(__name__, template_folder=folder, static_folder=folder)
app.add_url_rule('/', 'index', index, methods=['GET', 'POST'])
app.add_url_rule('/test', 'test', test)
app.add_url_rule('/save_answer', 'save_answer', save_answers, methods=['POST'])
app.add_url_rule('/result', 'result', result)
app.config['SECRET_KEY'] = 'VeryStrongkey'

if __name__ == '__main__':
    app.run(debug=True)