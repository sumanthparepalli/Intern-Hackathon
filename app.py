from flask import Flask, render_template
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view='login'
migrate = Migrate(app, db)

import routes, models


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': models.User, 'Store': models.Store, 'UserAddress': models.UserAddress,
            'Product': models.Product, 'Category': models.Category, 'Inventory': models.Inventory,
            'Order': models.Order, 'OrderDetails': models.OrderDetails, 'CardInfo': models.CardInfo,
            'TransactionDetails': models.TransactionDetails, 'CreditScheme': models.CreditScheme,
            'CategoryProductMap': models.CategoryProductMap, 'UserStoreMap': models.UserStoreMap,
            'PrepaidScheme': models.PrepaidScheme, 'SubInventory': models.SubInventory,
            'PaymentProcessing': models.PaymentProcessing, 'app':app}


if __name__ == '__main__':
    app.run(debug=True)
