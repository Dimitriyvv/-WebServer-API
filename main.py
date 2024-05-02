from flask import Flask, request, jsonify, render_template, g, flash, abort, url_for, session, redirect
import os
import sqlite3

app = Flask(__name__)
todo_list = []


class Task:
    def init(self, task_name, task_time):
        self.task_name = task_name
        self.task_time = task_time


@app.errorhandler(404)
def error404(error):
    return render_template('error404.html')


@app.route("/")
def home():
    return render_template('index.html', tasks=todo_list)


@app.route("/login", methods=["POST", "GET"])
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', usernme=session['userLogged']))
    elif request.method == "POST" and request.form['username'] == "selfedu" and request.form['password'] == "123":
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=['userLogged']))

    return render_template('login.html')


@app.route("/register")
def register():
    return render_template('register.html')


@app.route("/profile/<username>")
def profile(username):
    return f"Профиль пользователя: {username}"


if __name__ == '__main__':
    app.run(debug=True)