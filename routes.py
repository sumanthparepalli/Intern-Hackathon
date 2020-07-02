import json
from datetime import datetime

from sqlalchemy import func
from werkzeug.urls import url_parse

from app import app, db
from flask import render_template, redirect, url_for, flash, request, jsonify, session, abort
from forms import LoginForm, StoreRegistrationForm, UserRegistrationForm, AddressForm, DonationForm, CartForm, CardForm
from flask_login import login_required, login_user, logout_user, current_user

from merchant_operations import merchant_get_operations, merchant_update_operations
from merchant_selection_per_product.wrapper_for_data import input_for_wrapper

from models import User, Store, UserStoreMap, UserAddress, Product, Inventory, Order, OrderDetails, PrepaidScheme, \
    CardInfo, TransactionDetails, SubInventory
from order_processing import sub_inventory_update_merchant_side
from payment_service import *


@app.route('/index', methods=['get'])
@app.route('/', methods=['get'])
@login_required
def index():
    if User.query.get(current_user.get_id()).userType == 0:
        addressId = request.args.get('address')
        if addressId is not None:
            try:
                data = input_for_wrapper(int(addressId), int(db.session.query(UserAddress).get(addressId).zipcode))
                session['data'] = data
                session['addressId'] = addressId
                app.logger.info('added data in session:' + json.dumps(session['data']))
            except:
                flash("Sorry, we don't have any stores registered yet in your location")
                return render_template('index.html', title='Homepage')
            return render_template('index.html', title='Home', products=data)
    elif current_user.userType == 1:
        return redirect(url_for('dashboard'))
    else:
        return 'Choose an address to View available products'
    return render_template('index.html', title="Homepage")


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
    session.clear()
    logout_user()
    flash('Logged out successfully')
    return redirect(url_for('login'))


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
        flash('Register Successfully. Sign-in to continue')
        return redirect(url_for('login'))
    return render_template('register.html', title="Register", form=form, type=user_type)


@app.route('/add-address', methods=['get', 'post'])
@login_required
def add_address():
    if User.query.get(current_user.get_id()).userType == 1:
        return abort(403)
    form = AddressForm()
    if form.validate_on_submit():
        uad = UserAddress(
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            street=form.street.data,
            city=form.city.data,
            zipcode=form.zipcode.data,
            state=form.state.data,
            country=form.country.data
        )
        uad.userId = current_user.get_id()
        db.session.add(uad)
        db.session.commit()
        flash('Address Added')
        return redirect(url_for('index'))
    return render_template('add_address.html', form=form, title='Add Address')


@app.route('/products', methods=['get'])
def show_products():
    products = db.session.query(Product).all()
    prices = [
        float(db.session.query(db.func.min(Inventory.price)).filter(Inventory.productId == i.productId).first()[0])
        for i in products
    ]
    return render_template('products.html', title='Products', zipped=zip(products, prices))


@app.route('/products/<productId>', methods=['get'])
def product_page(productId):
    if 'data' in session:
        data = session['data']
        print(data)
        storeIds = [j[0] for j in data[productId]]
        print(storeIds)
        sellers_prices_discount = db.session \
            .query(Store.storeId, Store.storeName, Inventory.price, Inventory.discount,
                   Inventory.quantity).filter(Inventory.productId == productId) \
            .filter(Inventory.storeId == Store.storeId) \
            .filter(Store.storeId.in_(storeIds)) \
            .filter(Inventory.quantity > 0) \
            .group_by(Store.storeId).all()
    else:
        sellers_prices_discount = db.session \
            .query(Inventory.storeId, Store.storeName, Inventory.price, Inventory.discount,
                   Inventory.quantity).filter(Inventory.productId == productId) \
            .filter(Inventory.storeId == Store.storeId) \
            .filter(Store.storeId == Inventory.storeId) \
            .filter(Inventory.quantity > 0) \
            .group_by(Store.storeId).all()
    product = db.session.query(Product).get(productId)
    print(sellers_prices_discount)
    return render_template('product_info.html', product=product, sellers=sellers_prices_discount,
                           title=product.productName)


@app.route('/cart/<productId>', methods=['post'])
def add_to_cart(productId):
    bdata = request.data
    res = json.loads(bdata.decode("utf-8"))
    storeId = res['storeId']
    if 'addressId' in session:
        addressId = session['addressId']
    else:
        return json.dumps({'message': 'Address Not selected'}), 500
    qty = res['quantity']
    userId = current_user.get_id()
    price, discount = db.session.query(Inventory.price, Inventory.productId).filter(
        Inventory.storeId == storeId).filter(
        Inventory.productId == productId).first()
    fin_price = price * (100 - discount) / 100
    orderId = db.session.query(Order.orderId).filter(Order.userId == userId, Order.status == False).first()
    if orderId is None:
        new_order = Order(userId=userId, dateOfOrder=datetime.now(), totalAmount=0, shippingAddressId=addressId,
                          billingAddressId=addressId, orderCount=0, status=False)
        db.session.add(new_order)
        orderId = db.session.query(Order.orderId).filter(Order.userId == userId).filter(Order.status == False).first()[
            0]
    else:
        orderId = orderId[0]
    ord = OrderDetails.query.get((orderId, productId, storeId))
    if ord is None:
        ord = OrderDetails(orderId=orderId, productId=productId, storeId=storeId, quantity=qty,
                           priceAfterDiscount=fin_price)
        db.session.add(ord)
    else:
        ord.quantity += int(qty)
        ord.priceAfterDiscount += fin_price
    order = db.session.query(Order).get(orderId)
    order.totalAmount += fin_price * int(qty)
    order.orderCount = db.session.query(OrderDetails).filter(OrderDetails.orderId == orderId).count()
    order.dateOfOrder = datetime.now()
    db.session.commit()
    app.logger.info(ord.__repr__() + 'added')
    return json.dumps({'message': 'ok'}), 200


# @app.route('/cart', methods=['get'])
# @login_required
# def show_cart():
#     userId = current_user.get_id()
#     order = db.session.query(Order).filter(Order.userId == userId).filter(Order.status == False).first()
#     if order is None:
#         return "Empty Cart"
#     ordDetails = order.orderDetails.all()
#     product_seller = [
#         [db.session.query(Product).get(i.productId).productName, db.session.query(Store).get(i.storeId).storeName]
#         for i in ordDetails
#     ]
#     items = zip(ordDetails, product_seller)
#     return render_template('cart.html', image='', title="Cart", items=items)


@app.route("/orders", methods=['get'])
@login_required
def orders():
    if current_user.userType == 1:
        return abort(403)
    ord = current_user.orders
    ordDetails = [
        zip(db.session.query(OrderDetails).filter(OrderDetails.orderId == i.orderId).all(),
            [db.session.query(Product).get(p.productId).productName for p in
             db.session.query(OrderDetails).filter(OrderDetails.orderId == i.orderId).all()])
        for i in ord
    ]

    print(list(zip(ord, ordDetails)))
    return render_template('orders.html', title='Orders', ordDetails=zip(ord, ordDetails))


@app.route("/donations", methods=['get'])
@login_required
def donate():
    if current_user.userType == 1:
        return abort(403)
    data = db.session.query(Store.storeId, Store.storeName, PrepaidScheme.amount, PrepaidScheme.discount).join(
        Store.prepaidSchemes).all()
    form = DonationForm()
    return render_template('credit_scheme.html', title='Donations', data=data, form=form)


@app.route("/cart", methods=['get', 'post'])
@login_required
def cart():
    if current_user.userType == 1:
        return abort(403)
    if request.method == 'POST':
        form = CartForm()
        if form.validate_on_submit():
            orderId = form.orderId.data
            productId = form.productId.data
            storeId = form.storeId.data
            quantity = form.quantity.data
            ordDetails = db.session.query(OrderDetails).get((int(orderId), int(productId), int(storeId)))
            inventory = db.session.query(Inventory).get((int(storeId), int(productId)))
            ordDetails.quantity = int(quantity)
            ordDetails.priceAfterDiscount = float(inventory.price) * ((100 - inventory.discount) / 100) * int(quantity)
            order = db.session.query(Order).get(orderId)
            order.totalAmount = \
                db.session.query(func.sum(OrderDetails.priceAfterDiscount)).filter(
                    OrderDetails.orderId == orderId).first()[
                    0]
            db.session.commit()
            return redirect('/cart'), 200
    if request.args.get('orderId') is not None and request.args.get('storeId') is not None and request.args.get(
            'productId') is not None and request.args.get('action') == 'delete':
        orderId = request.args.get('orderId')
        storeId = request.args.get('storeId')
        productId = request.args.get('productId')
        ordDetails = db.session.query(OrderDetails).get((int(orderId), int(productId), int(storeId)))
        db.session.delete(ordDetails)
        db.session.commit()
        return redirect('/cart')
    orderId = db.session.query(Order.orderId).filter(Order.userId == current_user.get_id(),
                                                     Order.status == False).first()
    if orderId is None:
        return "Empty cart"
    else:
        orderId = orderId[0]
        ordDetails = db.session.query(OrderDetails).filter(OrderDetails.orderId == orderId).all()
        forms = [CartForm() for _ in ordDetails]
        productNames = [db.session.query(Product).get(i.productId).productName for i in ordDetails]
        print(list(zip(ordDetails, productNames, forms)))
    return render_template("cart.html", data=zip(ordDetails, productNames, forms),
                           total=db.session.query(Order.totalAmount).filter(Order.orderId == orderId).first()[0])


@app.route('/checkout', methods=['get', 'post'])
@login_required
def checkout():
    form = CardForm()
    if request.method == 'POST':
        print('in op')
        if form.validate_on_submit():
            print('in Post')
            cardNumber = form.cardNumber.data
            nameOnCard = form.nameOnCard.data
            expMonth = form.expMonth.data
            expYear = form.expYear.data
            cvv = form.cvv.data
            card = CardInfo(cardNumber=cardNumber, nameOnCard=nameOnCard, expMonth=expMonth, expYear=expYear,
                            userId=current_user.get_id())
            db.session.add(card)
            db.session.commit()
            card = db.session.query(CardInfo).filter(CardInfo.cardNumber == cardNumber).first()
            return redirect(url_for('pay_checkout', cardId=card.cardId))
    savedCards = current_user.cards
    return render_template('checkout.html', form=form, savedCards=savedCards)


@app.route('/pay-checkout/<cardId>', methods=['get'])
@login_required
def pay_checkout(cardId):
    if current_user.userType == 1:
        return abort(403)
    order = current_user.orders.filter(Order.status == False).first()
    amount = order.totalAmount
    orderId = order.orderId
    card = CardInfo.query.get(cardId)
    addressId = order.shippingAddressId
    address = UserAddress.query.get(addressId)
    response = pullFundsCall(float(amount), str(card.expYear) + '-' + str(card.expMonth), "USD", card.cardNumber,
                             address.street, str(address.zipcode))
    print(response)
    if 'errorMessage' in response:
        flash(response['errorMessage'].split('.')[1])
        return redirect(url_for('orders'))
    else:
        Tid = response['transactionIdentifier']
        userId = current_user.get_id()
        status = True
        trans = TransactionDetails(transactionId=Tid, userId=userId, orderId=orderId, amount=float(amount),
                                   status=status)
        order.status = True
        db.session.add(trans)
        db.session.commit()
        return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    if User.query.get(current_user.get_id()).userType == 1:
        return render_template("dashboard.html", user=current_user)
    else:
        return abort(403)


@app.route('/getStore', methods=["GET", "POST"])
def get_store():
    if request.method == 'POST':
        user = request.data
        res_dict = json.loads(user.decode('utf-8'))
        userId = res_dict['userId']
        user_store_list = merchant_get_operations.get_store_list(userId)
        print(user_store_list)
        store_list_json = json.dumps(user_store_list)
        return store_list_json


@app.route('/getInventory', methods=["GET", "POST"])
def get_inventory():
    if request.method == 'POST':
        user = request.data
        res_dict = json.loads(user.decode('utf-8'))
        storeId = res_dict['storeId']
        inventory_list = merchant_get_operations.get_inventory_details(storeId)
        inventory_list = json.dumps(inventory_list)
        print(inventory_list)
        return inventory_list


@app.route('/updateInventory', methods=["GET", "POST"])
def update_inventory():
    if request.method == 'POST':
        user = request.data
        res_dict = json.loads(user.decode('utf-8'))
        merchant_update_operations.update_inventory_record(res_dict)
        return {"message": "Inventory updated successfully"}


@app.route('/getSubInventory', methods=["GET", "POST"])
def get_sub_inventory():
    if request.method == "POST":
        user = request.data
        res_dict = json.loads(user.decode('utf-8'))
        storeId = res_dict['storeId']
        sub_inventory_list = merchant_get_operations.get_sub_inventory_details(storeId)
        sub_inventory_list = json.dumps(sub_inventory_list)
        return sub_inventory_list


@app.route('/updateSubInventory', methods=["GET", "POST"])
def update_sub_inventory():
    if request.method == 'POST':
        sub_inventory = request.data
        sub_inventory_dict = json.loads(sub_inventory.decode('utf-8'))
        for records in sub_inventory_dict:
            delivery = db.session.query(SubInventory.delivery).filter(SubInventory.productId == records["productId"]) \
                .filter(SubInventory.orderId == records["orderId"]).filter(
                SubInventory.storeId == records["storeId"]).first()
            if delivery == None or delivery[0] == records["delivery"]:
                pass
            else:
                sub_inventory_update_merchant_side.update_inventory_record(records["storeId"], records["productId"],
                                                                           records["orderId"])
        return {"message": "Sub Inventory updated successfully"}


@app.route('/getCustomerList', methods=['GET', 'POST'])
def get_customer_list():
    if request.method == 'POST':
        user = request.data
        res_dict = json.loads(user.decode('utf-8'))
        userId = res_dict['userId']
        user_store_list = merchant_get_operations.get_credit_scheme_details(userId)
        store_list_json = json.dumps(user_store_list)
        return store_list_json


@app.route('/getCreditSchemeDetails', methods=['GET', 'POST'])
def get_store_scheme_details():
    if request.method == 'POST':
        user = request.data
        res_dict = json.loads(user.decode('utf-8'))
        userId = res_dict['userId']
        credit_scheme_store_list = merchant_get_operations.get_credit_scheme_details_based_on_merchant(userId)
        credit_scheme_store_list = json.dumps(credit_scheme_store_list)
        print(credit_scheme_store_list)
        return credit_scheme_store_list


@app.route('/getPrepaidSchemeDetails', methods=["GET", "POST"])
def get_prepaid_scheme_details():
    if request.method == 'POST':
        user = request.data
        res_dict = json.loads(user.decode('utf-8'))
        userId = res_dict['userId']
        print(userId)
        prepaid_scheme_store_list = merchant_get_operations.get_prepaid_scheme_details(userId)
        prepaid_scheme_store_list = json.dumps(prepaid_scheme_store_list)
        return prepaid_scheme_store_list
