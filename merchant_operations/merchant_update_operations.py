"""
    This script is used to update details to the merchants records in the database
"""
from app import app, db
import decimal
from models import *


# used to update quantity in the inventory
def update_inventory_quantity(store_id, product_id, quantity):
    inventory_record = db.session.query(Inventory).filter(Inventory.storeId == store_id) \
        .filter(Inventory.productId == product_id).first()
    inventory_record.quantity += quantity
    db.session.commit()


# used to update the price in the inventory
def update_inventory_price(store_id, product_id, price):
    inventory_record = db.session.query(Inventory).filter(Inventory.storeId == store_id) \
        .filter(Inventory.productId == product_id).first()
    inventory_record.price = decimal.Decimal(price)
    db.session.commit()


# used to update the discount in the inventory
def update_inventory_discount(store_id, product_id, discount):
    inventory_record = db.session.query(Inventory).filter(Inventory.storeId == store_id) \
        .filter(Inventory.productId == product_id).first()
    inventory_record.discount = discount
    db.session.commit()


# used to update set of records in the inventory
def update_inventory_record(inventory_dict):
    for records in inventory_dict:
        inventory_object = db.session.query(Inventory).filter(Inventory.storeId == records["storeId"]) \
            .filter(Inventory.productId == records["productId"]).first()
        inventory_object.price = decimal.Decimal(records["price"])
        inventory_object.discount = records["discount"]
        inventory_object.quantity = records["quantity"]
    db.session.commit()


if __name__ == "__main__":
    update_inventory_discount(1, 1, 10)
