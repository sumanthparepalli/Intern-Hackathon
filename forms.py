from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from app import db
from models import User, UserAddress, CreditScheme, Inventory


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class StoreRegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    # userType = BooleanField('Store Account')
    mobile = StringField('Mobile no')
    ######################################
    storeName = StringField('storeName', validators=[DataRequired()])
    country = StringField('country', validators=[DataRequired()])
    state = StringField('state', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    street = StringField('street', validators=[DataRequired()])
    zipCode = StringField('zipCode', validators=[DataRequired()])
    latitude = StringField('latitude', validators=[DataRequired()])
    longitude = StringField('longitude', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

    def validate_mobile(self, mobile):
        if not mobile is None and len(mobile) != 10:
            return ValidationError('Should contain 10 digits')


class UserRegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    mobile = StringField('Mobile no')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

    def validate_mobile(self, mobile):
        if not mobile is None and len(mobile) != 10:
            return ValidationError('Should contain 10 digits')


class AddressForm(FlaskForm):
    latitude = FloatField('latitude', validators=[DataRequired()])
    longitude = FloatField('longitude', validators=[DataRequired()])
    street = StringField('street', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    zipcode = IntegerField('zipcode', validators=[DataRequired()])
    state = StringField('state', validators=[DataRequired()])
    country = StringField('country', validators=[DataRequired()])
    submit = SubmitField('Add Address')


class DonationForm(FlaskForm):
    amount = IntegerField('amount', validators=[DataRequired()])
    submit = SubmitField('Donate')
    storeId = IntegerField('storeId')

    def validate_amount(self, amount):
        maxamt = db.session.query(CreditScheme.amount).filter(CreditScheme.storeId == self.storeId).first()[0]
        if amount > maxamt or amount <= 0:
            raise ValidationError("Invalid amount")


class CartForm(FlaskForm):
    orderId = StringField('orderId', validators=[DataRequired()])
    productId = StringField('productId', validators=[DataRequired()])
    storeId = StringField('storeId', validators=[DataRequired()])
    quantity = IntegerField('quantity', validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_quantity(self, quantity):
        maxqty = db.session.query(Inventory).get((int(self.storeId.data), int(self.productId.data))).quantity
        if quantity.data > maxqty:
            raise ValidationError("Merchant doesn't have the requested quantity")
        elif quantity.data <= 0:
            raise ValidationError("Invalid quantity")


class CardForm(FlaskForm):
    cardNumber = StringField('Card Number', validators=[DataRequired()])
    nameOnCard = StringField('Name on Card', validators=[DataRequired()])
    expMonth = IntegerField('expMonth', validators=[DataRequired()])
    expYear = IntegerField('expYear', validators=[DataRequired()])
    cvv = PasswordField('cvv', validators=[DataRequired()])
    ConfirmPayment = SubmitField('Confirm Payment')

    def validate_cardNumber(self, cardNumber):
        if not cardNumber.data.isdigit():
            raise ValidationError("Invalid Card Number")

    def validate_expMonth(self, expMonth):
        if expMonth.data < 1 or expMonth.data > 12:
            raise ValidationError("Invalid Month")

    def validate_expYear(self, expYear):
        if expYear.data < datetime.now().year:
            raise ValidationError("Invalid expiry")

    def validate_cvv(self, cvv):
        if len(cvv.data) != 3 or not cvv.data.isdigit():
            raise ValidationError("Invalid cvv")
