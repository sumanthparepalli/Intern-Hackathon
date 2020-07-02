from werkzeug.urls import url_parse

from app import app, db
from flask import render_template, redirect, url_for, flash, request
from forms import LoginForm, StoreRegistrationForm, UserRegistrationForm
from flask_login import login_required, login_user, logout_user, current_user
from merchant_operations import merchant_get_operations,merchant_update_operations
from order_processing import sub_inventory_update_merchant_side
import json

from models import User, Store, UserStoreMap, SubInventory


@app.route('/', methods=['get'])
@app.route('/index', methods=['get'])
def index():
    return render_template('index.html', title="Homepage", user="Sumanth")


@app.route("/login", methods=['get', 'post'])
def login():
    if current_user.is_authenticated:
        if User.query.get(current_user.get_id()).userType == 1:
            return redirect(url_for('dashboard'))
        else:
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
            if User.query.get(current_user.get_id()).userType == 1:
                next_page=url_for('dashboard')
            else:
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

@app.route('/dashboard')
@login_required
def dashboard():
    if User.query.get(current_user.get_id()).userType == 1:
        return render_template("dashboard.html",user=current_user)

@app.route('/getStore',methods=["GET","POST"])
def get_store():
    if request.method == 'POST':
        user = request.data
        res_dict = json.loads(user.decode('utf-8')) 
        userId = res_dict['userId']
        user_store_list = merchant_get_operations.get_store_list(userId)
        print(user_store_list)
        store_list_json = json.dumps(user_store_list)
        return store_list_json

@app.route('/getInventory',methods=["GET","POST"])
def get_inventory():
    if request.method == 'POST':
        user = request.data
        res_dict = json.loads(user.decode('utf-8'))
        storeId = res_dict['storeId']
        inventory_list = merchant_get_operations.get_inventory_details(storeId)
        inventory_list = json.dumps(inventory_list)
        print(inventory_list)
        return inventory_list

@app.route('/updateInventory',methods=["GET","POST"])
def update_inventory():
    if request.method=='POST':
        user = request.data
        res_dict = json.loads(user.decode('utf-8'))
        merchant_update_operations.update_inventory_record(res_dict)
        return {"message":"Inventory updated successfully"}

@app.route('/getSubInventory',methods=["GET","POST"])
def get_sub_inventory():
    if request.method == "POST":
        user = request.data
        res_dict = json.loads(user.decode('utf-8'))
        storeId = res_dict['storeId']
        sub_inventory_list = merchant_get_operations.get_sub_inventory_details(storeId)
        sub_inventory_list = json.dumps(sub_inventory_list)
        return sub_inventory_list

@app.route('/updateSubInventory',methods=["GET","POST"])
def update_sub_inventory():
    if request.method=='POST':
        sub_inventory = request.data
        sub_inventory_dict = json.loads(sub_inventory.decode('utf-8'))
        for records in sub_inventory_dict:
            delivery = db.session.query(SubInventory.delivery).filter(SubInventory.productId==records["productId"])\
                .filter(SubInventory.orderId == records["orderId"]).filter(SubInventory.storeId == records["storeId"]).first()
            if delivery == None or delivery[0]==records["delivery"]:
                pass
            else:
                sub_inventory_update_merchant_side.update_inventory_record(records["storeId"],records["productId"],records["orderId"])
        return {"message":"Sub Inventory updated successfully"}


@app.route('/getCustomerList',methods = ['GET','POST'])
def get_customer_list():
    if request.method=='POST':
        user = request.data
        res_dict = json.loads(user.decode('utf-8')) 
        userId = res_dict['userId']
        user_store_list = merchant_get_operations.get_credit_scheme_details(userId)
        store_list_json = json.dumps(user_store_list)
        return store_list_json

@app.route('/getCreditSchemeDetails',methods=['GET','POST'])
def get_store_scheme_details():
    if request.method=='POST':
        user = request.data
        res_dict = json.loads(user.decode('utf-8'))
        userId = res_dict['userId']
        credit_scheme_store_list = merchant_get_operations.get_credit_scheme_details_based_on_merchant(userId)
        credit_scheme_store_list = json.dumps(credit_scheme_store_list)
        print(credit_scheme_store_list)
        return credit_scheme_store_list

@app.route('/getPrepaidSchemeDetails',methods=["GET","POST"])
def get_prepaid_scheme_details():
    if request.method == 'POST':
        user = request.data
        res_dict = json.loads(user.decode('utf-8'))
        userId = res_dict['userId']
        print(userId)
        prepaid_scheme_store_list = merchant_get_operations.get_prepaid_scheme_details(userId)
        prepaid_scheme_store_list = json.dumps(prepaid_scheme_store_list)
        return prepaid_scheme_store_list

@app.route('/register', methods=['get', 'post'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user_type = request.args.get('type')
    form = StoreRegistrationForm() if user_type == 'store' else UserRegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, username=form.username.data, email=form.email.data, mobile=form.mobile.data)
        user.set_password(form.password.data)
        if user_type == 'store':
            user.userType = 1
            store = Store(storeName=form.storeName.data, country=form.country.data, state=form.state.data,
                          city=form.city.data, street=form.street.data, zipCode=form.zipCode.data,
                          latitude=form.latitude.data, longitude=form.longitude.data)
            db.session.add(store)
            db.session.add(user)
            usm = UserStoreMap(userId=User.query.filter_by(username=form.username.data).first().id,
                               storeId=Store.query.filter_by(latitude=form.latitude.data,
                                                             longitude=form.longitude.data).first().storeId)
            # usm = UserStoreMap(userId=user.id, storeId=store.storeId)
            db.session.add(usm)
        else:
            user.userType = 0
            db.session.add(user)
        db.session.commit()
        flash('Sign-in to continue')
        return redirect(url_for('login'))
    return render_template('register.html', title="Register", form=form, type=user_type)
