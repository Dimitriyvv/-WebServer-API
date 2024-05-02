import math
import sqlite3
import os
import time

from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask import Flask, render_template, request, g, flash, abort, session, redirect, url_for
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash

todo_list = []
DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = '8c3c8a5f486efd6830083d63f24e456d9503f1509504d29a'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

login_manager = LoginManager(app)


class UserLogin:
    def fromDB(self, user_id, db):
        self.__user = db.getUser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.__user['id'])


def getMenu(self):
    sql = '''SELECT * FROM mainmenu'''
    try:
        self.__cur.execute(sql)
        res = self.__cur.fetchall()
        if res: return res
    except:
        print('Ошибка чтения из БД')
    return []


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None


@app.before_request
def before_request():
    global dbase

    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route("/")
def index():
    return render_template('index.html', tasks=todo_list, menu=dbase.getMenu())


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user)
            login_user(userlogin)
            return redirect(url_for('index'))

        flash("Неверная пара логин/пароль", "error")

    return render_template("login.html", menu=dbase.getMenu(), title="Авторизация")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        session.pop('_flashes', None)
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
                and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'], request.form['email'], hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Неверно заполнены поля", "error")

    return render_template("register.html", menu=dbase.getMenu(), title="Регистрация")


def addUser(self, name, email, hpsw):
    try:
        self.__cur.execute(f"SELECT COUNT() as `count` FROM users WHERE email LIKE '{email}'")
        res = self.__cur.fetchone()
        if res['count'] > 0:
            print("Пользователь с таким email уже существует")
            return False

        tm = math.floor(time.time())
        self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, ?)", (name, email, hpsw, tm))
        self.__db.commit()
    except sqlite3.Error as e:
        print("Ошибка добавления пользователя в БД " + str(e))
        return False

    return True

def getUser(self, user_id):
    try:
        self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
        res = self.__cur.fetchone()
        if not res:
            print("Пользователь не найден")
            return False

        return res
    except sqlite3.Error as e:
        print("Ошибка получения данных из БД " + str(e))

    return False


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)


@app.route('/profile')
@login_required
def profile():
    return f"""<a href="{url_for('logout')}">Выйти из профиля</a>
                user info: {current_user.get_id()}"""

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
