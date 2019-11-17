import psycopg2
conn = psycopg2.connect(dbname='recomendation', user='student', password='student', host='localhost')
cursor = conn.cursor()

def user_exists(id_user):
    cursor.execute('SELECT id_user FROM users WHERE id_user = {}'.format(id_user))
    return True if len([row for row in cursor])>0 else False

def auth_user(user_id):
    cursor.execute("INSERT INTO users(id_user) VALUES ({})".format(user_id))

def story(id_user, question, answer):
    if len(answer) > 499:
        answer = answer[:498]
    if len(question) > 499:
        question = question[:498]
    cursor.execute("INSERT INTO story(id_user, question, answer) VALUES ({}, '{}', '{}')".format(id_user, str(question), str(answer)))    