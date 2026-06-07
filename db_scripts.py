import sqlite3
from random import shuffle

db_name = 'quiz.sqlite'

conn = None
cursor = None

def get_quises():
    query = 'SELECT * FROM quiz ORDER BY id'
    open()
    cursor.execute(query)
    result = cursor.fetchall()
    close()
    return result

def open():
    global conn, cursor
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')
    except sqlite3.Error as e:
        print(f"Ошибка подключения к БД: {e}")

def close():
    if conn and cursor:
        cursor.close()
        conn.close()

def do(query, params=None):
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка выполнения запроса: {e}")
        conn.rollback()

def clear_db():
    open()
    do('DROP TABLE IF EXISTS quiz_content')
    do('DROP TABLE IF EXISTS question')
    do('DROP TABLE IF EXISTS quiz')
    close()

def create():
    open()
    do('''
        CREATE TABLE IF NOT EXISTS quiz (
            id INTEGER PRIMARY KEY,
            name VARCHAR
        )
    ''')
    do('''
        CREATE TABLE IF NOT EXISTS question (
            id INTEGER PRIMARY KEY,
            question VARCHAR,
            answer VARCHAR,
            wrong1 VARCHAR,
            wrong2 VARCHAR,
            wrong3 VARCHAR
        )
    ''')
    do('''
        CREATE TABLE IF NOT EXISTS quiz_content (
            id INTEGER PRIMARY KEY,
            quiz_id INTEGER,
            question_id INTEGER,
            FOREIGN KEY (quiz_id) REFERENCES quiz (id),
            FOREIGN KEY (question_id) REFERENCES question (id)
        )
    ''')
    close()

def add_questions():
    questions = [
        ('Сколько месяцев в году имеют 28 дней?', 'Все', 'Один', 'Ни одного', 'Два'),
        ('Каким станет зеленый утес, если упадет в Красное море?', 'Мокрым', 'Красным', 'Не изменится', 'Фиолетовым'),
        ('Какой рукой лучше размешивать чай?', 'Ложкой', 'Правой', 'Левой', 'Любой'),
        ('Что не имеет длины, глубины, ширины, высоты, а можно измерить?', 'Время', 'Глупость', 'Море', 'Воздух'),
        ('Когда сетью можно вытянуть воду?', 'Когда вода замерзла', 'Когда нет рыбы', 'Когда уплыла золотая рыбка', 'Когда сеть порвалась'),
        ('Что больше слона и ничего не весит?', 'Тень слона', 'Воздушный шар', 'Парашют', 'Облако')
    ]
    open()
    cursor.executemany('''
        INSERT INTO question (question, answer, wrong1, wrong2, wrong3)
        VALUES (?, ?, ?, ?, ?)
    ''', questions)
    conn.commit()
    close()

def add_quiz():
    quizes = [
        ('Своя игра',),
        ('Кто хочет стать миллионером?',),
        ('Самый умный',)
    ]
    open()
    cursor.executemany('INSERT INTO quiz (name) VALUES (?)', quizes)
    conn.commit()
    close()

def quiz_content():
    open()
    query = 'INSERT INTO quiz_content (quiz_id, question_id) VALUES (?,?)'
    while True:
        user_input = input('Добавить связь (y / n)? ').strip().lower()
        if user_input == 'n':
            break
        if user_input != 'y':
            print("Введите 'y' или 'n'.")
            continue
        try:
            quiz_id = int(input('id викторины: '))
            question_id = int(input('id вопроса: '))
            cursor.execute(query, [quiz_id, question_id])
            conn.commit()
            print("Связь добавлена.")
        except ValueError:
            print("Введите числовые значения.")
        except sqlite3.IntegrityError as e:
            print(f"Ошибка целостности (неверный id): {e}")
    close()

def get_question_after(question_id=0, quiz_id=1):
    open()
    query = '''
        SELECT 
            quiz_content.id, 
            question.question, 
            question.answer, 
            question.wrong1, 
            question.wrong2, 
            question.wrong3
        FROM question, quiz_content
        WHERE question.id = quiz_content.question_id
          AND quiz_content.quiz_id = ?
          AND quiz_content.id > ?
        ORDER BY quiz_content.id
        LIMIT 1
    '''
    cursor.execute(query, [quiz_id, question_id])
    result = cursor.fetchone()
    close()
    return result

def show(table):
    query = f'SELECT * FROM {table}'
    open()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        print(f"\n--- Таблица: {table} ---")
        for row in rows:
            print(row)
    except sqlite3.Error as e:
        print(f"Ошибка при чтении таблицы {table}: {e}")
    finally:
        close()

def show_tables():
    show('quiz')
    show('question')
    show('quiz_content')

def check_answer(q_id, ans_text):
    query = '''SELECT question.answer
            FROM quiz_content, question
            WHERE quiz_content.id = ?
            AND quiz_content.question_id = question.id'''
    open()
    cursor.execute(query, (q_id,))
    result = cursor.fetchone()
    close()
    if result is None: 
        return False
    else:
        return result[0] == ans_text

def main():
    clear_db()
    create()
    add_questions()
    add_quiz()
    print("Теперь свяжем вопросы с викториной.")
    quiz_content()
    show_tables()
    print("\nСледующий вопрос после id=3 в викторине id=1:")
    print(get_question_after(3, 1))

if __name__ == "__main__":
    main()