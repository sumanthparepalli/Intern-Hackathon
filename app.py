from flask import Flask, render_template
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'
migrate = Migrate(app, db)

import routes, models, errors


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': models.User, 'Store': models.Store, 'UserAddress': models.UserAddress,
            'Product': models.Product, 'Category': models.Category, 'Inventory': models.Inventory,
            'Order': models.Order, 'OrderDetails': models.OrderDetails, 'CardInfo': models.CardInfo,
            'TransactionDetails': models.TransactionDetails, 'CreditScheme': models.CreditScheme,
            'CategoryProductMap': models.CategoryProductMap, 'UserStoreMap': models.UserStoreMap,
            'PrepaidScheme': models.PrepaidScheme, 'SubInventory': models.SubInventory,
            'PaymentProcessing': models.PaymentProcessing, 'app': app}


if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Site Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handle = RotatingFileHandler('logs/site.log', maxBytes=10240, backupCount=5)
    file_handle.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handle.setLevel(logging.INFO)
    app.logger.addHandler(file_handle)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Site startup')

if __name__ == '__main__':
    app.run(debug=True)
