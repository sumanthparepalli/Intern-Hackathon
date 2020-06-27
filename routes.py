from werkzeug.urls import url_parse

from app import app, db
from flask import render_template, redirect, url_for, flash, request
from forms import LoginForm, RegistrationForm
from flask_login import login_required, login_user, logout_user, current_user

from models import User, Store, UserStoreMap


@app.route('/', methods=['get'])
@app.route('/index', methods=['get'])
def index():
    return render_template('index.html', title="Homepage", user="Sumanth")


@app.route("/login", methods=['get', 'post'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid Username or Password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template("login.html", form=form, title="Sign-in")


@app.route('/test-user')
@login_required
def userOnly():
    if User.query.get(current_user.get_id()).userType == 1:
        return "Not allowed to access"
    return "User - only access"


@app.route('/test-admin')
@login_required
def merchantOnly():
    if User.query.get(current_user.get_id()).userType == 0:
        return "Not allowed to access"
    return "store - only access"


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['get', 'post'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, username=form.username.data, email=form.email.data,
                    userType=form.userType.data, mobile=form.mobile.data)
        user.set_password(form.password.data)
        db.session.add(user)
        if form.userType:
            store = Store(storeName=form.storeName.data, country=form.country.data, state=form.state.data,
                          city=form.city.data, street=form.street.data, zipCode=form.zipCode.data,
                          latitude=form.latitude.data, longitude=form.longitude.data)
            db.session.add(store)
            usm = UserStoreMap(userId=User.query.filter_by(username=form.username.data).first().id,
                               storeId=Store.query.filter_by(latitude=form.latitude.data,
                                                             longitude=form.longitude.data).first().storeId)
            # usm = UserStoreMap(userId=user.id, storeId=store.storeId)
            db.session.add(usm)
        db.session.commit()
        return redirect(url_parse('/login'))
    return render_template('register.html', title="Register", form=form)
