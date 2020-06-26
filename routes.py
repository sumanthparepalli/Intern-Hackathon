from app import app
from flask import render_template, redirect, url_for, flash
from forms import LoginForm


@app.route('/', methods=['get'])
@app.route('/index', methods=['get'])
def index():
    return render_template('index.html', title="Homepage", user="Sumanth")


@app.route("/login", methods=['get', 'post'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash("Login requested for user {} with password {} ".format(form.username.data, form.password.data))
        return redirect(url_for('index'))
    return render_template("login.html", form=form, title="SIgn-in")
