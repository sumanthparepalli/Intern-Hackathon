from app import app, db
from models import SubInventory, Order, PaymentProcessing
import decimal

"""
This script is called every time a merchant approves the delivery of items to the spoc. 
This script accepts subInventory record and deletes it, updates the order count in the order table as well. 
Once all the order has been delivered to spoc a boolean is returned for notifying the user.
"""

def get_sub_inventory_based_on_store(store_id):
    query_results = db.session.query(SubInventory).filter(SubInventory.storeId == store_id).all()
    sub_inventory_list = []
    for records in query_results:
        sub_inventory = [records.storeId, records.productId, float(records.price), records.quantity, records.discount,
                         records.orderId, records.delivery]
        sub_inventory_list.append(sub_inventory)
    return sub_inventory_list


def change_order_count_in_order(order_id):
    query_results = db.session.query(Order).filter(Order.orderId == order_id).first()
    query_results.orderCount -= 1
    if (query_results.orderCount == 0):
        query_results.status = 1


def update_payment_processing(order_id, store_id):
    payment_records = db.session.query(PaymentProcessing).filter(PaymentProcessing.storeId == store_id).first()
    query_results = db.session.query(SubInventory).filter(SubInventory.storeId == store_id).filter(
        SubInventory.orderId == order_id) \
        .filter(SubInventory.delivery == 1).filter(SubInventory.paid == 0).all()
    for records in query_results:
        price = float(records.price)
        price = price - (price * records.discount) / 100
        payment_records.amount += decimal.Decimal(price)
        records.paid = 1


def update_inventory_record(store_id, product_id, order_id):
    query_results = db.session.query(SubInventory).filter(SubInventory.storeId == store_id).filter(
        SubInventory.orderId == order_id).filter(SubInventory.productId == product_id).filter(
        SubInventory.delivery == False).filter(SubInventory.paid == False).first()
    change_order_count_in_order(query_results.orderId)
    query_results.delivery = True
    update_payment_processing(order_id, store_id)
    db.session.commit()

if __name__ == "__main__":
    get_sub_inventory_based_on_store(1)
    update_inventory_record(1, 1, 1)