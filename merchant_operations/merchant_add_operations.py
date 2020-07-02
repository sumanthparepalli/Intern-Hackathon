"""
    This script is used for adding records into the db by the merchant
"""
from app import app,db
from models import *
import decimal

#inventory_record list to object for insertion
#inventory_record_list [storeId,productId,price,quantity,discount]
def get_inventory_object(inventory_record_list):
    inventory_object = Inventory()
    inventory_object.storeId = inventory_record_list[0]
    inventory_object.productId = inventory_record_list[1]
    inventory_object.price = decimal.Decimal(inventory_record_list[2])
    inventory_object.quantity = inventory_record_list[3]
    inventory_object.discount = inventory_record_list[4]
    return inventory_object

#adds a new record in inventory
def add_inventory_record(inventory_record_list):
    inventory_object = get_inventory_object(inventory_record_list)
    db.session.add(inventory_object)
    db.session.commit()

if __name__ == "__main__":
    add_inventory_record([1,6,100,100,10])