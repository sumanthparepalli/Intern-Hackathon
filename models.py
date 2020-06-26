from app import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"
    userId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(500), nullable=False, index=True)
    userType = db.Column(db.Boolean, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, index=True)
    mobile = db.Column(db.String(15))
    addresses = db.relationship('userAddress',
                                backref=db.backref('user', cascade='all, delete-orphan'),
                                lazy='Dynamic')
    orders = db.relationship('order',
                             backref=db.backref('user', cascade='all, delete-orphan'),
                             lazy='Dynamic')
    cards = db.relationship('cardInfo',
                            backref=db.backref('user', cascade='all, delete-orphan'),
                            lazy='Dynamic')
    transactions = db.relationship('TransactionDetails',
                                   backref=db.backref('user', cascade='all, delete-orphan'),
                                   lazy='Dynamic')
    creditStores = db.relationship("store", secondary="credit")
    StoresMapped = db.relationship("store", secondary="usm")

    def __repr__(self):
        return '<User {}>'.format(self.userId)


class UserAddress(db.Model):
    userId = db.Column(db.Integer, db.ForeignKey('users.userId'))
    addressId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    country = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    street = db.Column(db.String(100), nullable=False)
    zipcode = db.Column(db.String(10), nullable=False)
    latitude = db.Column(db.DECIMAL(12, 9), nullable=False)
    longitude = db.Column(db.DECIMAL(12, 9), nullable=False)

    def __repr__(self):
        return "<userAddress {}>".format(self.userId)


class Store(db.Model):
    storeId = db.Column(db.Integer, autoincrement=True, primary_key=True)
    storeName = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    street = db.Column(db.String(100), nullable=False)
    zipcode = db.Column(db.String(10), nullable=False)
    latitude = db.Column(db.DECIMAL(12, 9), nullable=False)
    longitude = db.Column(db.DECIMAL(12, 9), nullable=False)
    products = db.relationship("product", secondary="inventory")
    creditUsers = db.relationship("users", secondary="credit")
    usersMapped = db.relationship("users", secondary="usm")
    prepaidSchemes = db.relationship('PrepaidScheme',
                                     backref=db.backref('store', cascade='all, delete-orphan'),
                                     lazy='Dynamic')
    subInventories = db.relationship('SubInventory',
                                     backref=db.backref('store', cascade='all, delete-orphan'),
                                     lazy='Dynamic')
    paymentProcessings = db.relationship('paymentProcessing',
                                         backref=db.backref('store', cascade='all, delete-orphan'),
                                         lazy='Dynamic')

    def __repr__(self):
        return "<Store {}>".format(self.storeName)


class Product(db.Model):
    productId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    weight = db.Column(db.INTEGER)
    measurementType = db.Column(db.Boolean)
    Description = db.Column(db.String(100))
    stores = db.relationship("store", secondary="inventory")
    category = db.relationship("category", secondary="cpm")

    def __repr__(self) -> str:
        return "<Product {}".format(self.productId)


class Category(db.Model):
    categoryId = db.Column(db.Integer, autoincrement=True, primary_key=True)
    categoryName = db.Column(db.String(100), nullable=False)
    categoryDescription = db.Column(db.String(100))
    products = db.relationship("product", secondary="cpm")

    def __repr__(self):
        return "<Category {}>".format(self.categoryId)


class Inventory(db.Model):
    storeId = db.Column(db.Integer, db.ForeignKey('store.storeId'))
    productId = db.Column(db.Integer, db.ForeignKey('product.productId'))
    price = db.Column(db.DECIMAL(10000, 9), nullable=False)
    quantity = db.Column(db.Integer, db.CheckConstraint('quantity>=0'), nullable=False)
    discount = db.Column(db.Integer, default=0)
    stores = db.relationship(Store, backref=db.backref("inventory", cascade="all, delete-orphan"))
    product = db.relationship(Product, backref=db.backref("inventory", cascade="all, delete-orphan"))
    __table__args__ = (
        db.PrimaryKeyConstraint(storeId, productId)
    )

    def __repr__(self):
        return "<Inventory {} - {}>".format(self.storeId, self.productId)


class Order(db.Model):
    orderId = db.Column(db.Integer, autoincrement=True, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.userId'))
    dateOfOrder = db.Column(db.Date, default=datetime.utcnow)
    totalAmount = db.Column(db.DECIMAL(10000, 9))
    shippingAddressId = db.Column(db.Integer)
    billingAddressId = db.Column(db.Integer)
    orderCount = db.Column(db.Integer, default=0)
    status = db.Column(db.Boolean, default=False)
    orderDetails = db.relationship('orderDetails', backref=db.backref('order', cascade='all, delete-orphan'),
                                   lazy='Dynamic')

    def __repr__(self):
        return "order {}".format(self.orderId)


class OrderDetails(db.Model):
    orderId = db.Column(db.Integer, db.ForeignKey('order.orderId'))
    productId = db.Column(db.Integer, db.ForeignKey('product.productId'))
    storeId = db.Column(db.Integer, db.ForeignKey('store.storeId'))
    quantity = db.Column(db.Integer, db.CheckConstraint('quantity > 0'), nullable=False)
    priceAfterDiscount = db.Column(db.DECIMAL(10000, 9), nullable=False)
    __table__args__ = (
        db.PrimaryKeyConstraint(orderId, productId, storeId)
    )

    def __repr__(self):
        return "<OrderDetails {} - {} - {}>".format(self.orderId, self.productId, self.storeId)


class CardInfo(db.Model):
    cardNumber = db.Column(db.String(12), primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.userId'))
    expMonth = db.Column(db.Integer, db.CheckConstraint('expMonth > 0 and expMonth <13'), nullable=False)
    expYear = db.Column(db.Integer, nullable=False)
    nameOnCard = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return "<Card {}>".format(self.cardNumber)


class TransactionDetails(db.Model):
    transactionId = db.Column(db.String(100), primary_key=True)
    orderId = db.Column(db.Integer, db.ForeignKey('order.orderId'))
    userId = db.Column(db.Integer, db.ForeignKey('users.userId'))
    amount = db.Column(db.DECIMAL(10000, 9), nullable=False)
    status = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return "<Transaction {}>".format(self.transactionId)


class CreditScheme(db.Model):
    userId = db.Column(db.Integer, db.ForeignKey('users.userId'))
    storeId = db.Column(db.Integer, db.ForeignKey('store.storeId'))
    amount = db.Column(db.DECIMAL(10000, 9))
    users = db.relationship(User, backref=db.backref("credit", cascade="all, delete-orphan"))
    stores = db.relationship(Store, backref=db.backref("credit", cascade="all, delete-orphan"))
    __table__args__ = (
        db.PrimaryKeyConstraint(userId, storeId)
    )


class categoryProductMap(db.Model):
    categoryId = db.Column(db.Integer, db.ForeignKey('category.categoryId'))
    productId = db.Column(db.Integer, db.ForeignKey('product.productId'))
    categories = db.relationship(Category, backref=db.backref("cpm", cascade="all, delete-orphan"))
    products = db.relationship(Product, backref=db.backref("cpm", cascade="all, delete-orphan"))
    __table__args__ = (
        db.PrimaryKeyConstraint(categoryId, productId)
    )


class UserStoreMap(db.Model):
    userId = db.Column(db.Integer, db.ForeignKey('users.userId'))
    storeId = db.Column(db.Integer, db.ForeignKey('store.storeId'))
    users = db.relationship(User, backref=db.backref("usm", cascade="all, delete-orphan"))
    stores = db.relationship(Store, backref=db.backref("usm", cascade="all, delete-orphan"))
    __table__args__ = (
        db.PrimaryKeyConstraint(userId, storeId)
    )


class prepaidScheme(db.Model):
    storeId = db.Column(db.Integer, db.ForeignKey("store.storeId"), primary_key=True)
    amount = db.Column(db.DECIMAL(10000, 9))


class SubInventory(db.Model):
    storeId = db.Column(db.Integer, db.ForeignKey("store.storeId"))
    productId = db.Column(db.Integer, db.ForeignKey('product.productId'))
    price = db.Column(db.DECIMAL(10000, 9), nullable=False)
    quantity = db.Column(db.Integer, db.CheckConstraint('quantity > 0'), nullable=False)
    discount = db.Column(db.Integer, nullable=False)
    orderId = db.Column(db.Integer, db.ForeignKey('order.orderId'))
    delivery = db.Column(db.Boolean, default=False)
    __table__args = (
        db.PrimaryKeyConstraint(storeId, productId)
    )

    def __repr__(self):
        return "<SubInventory {}>".format(self.storeId, self.productId)


class paymentProcessing(db.Model):
    storeId = db.Column(db.Integer, db.ForeignKey("store.storeId"), primary_key=True)
    amount = db.Column(db.DECIMAL(10000, 9))
