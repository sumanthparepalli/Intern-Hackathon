from app import db
from models import Inventory, SubInventory, OrderDetails

"""
    This script is used to process an order. For a given OrderId that has been placed, the script will
    fetch the order details and transfer those items from inventory to subinventory for a merchant to deliver.
"""


def fetch_order_details(order_id):
    query_results = db.session.query(OrderDetails).filter(OrderDetails.orderId == order_id).all()

    order_details_list = []

    for records in query_results:
        order_details = [records.storeId, records.productId, records.orderId, records.quantity]
        order_details_list.append(order_details)
    print(order_details_list)
    return order_details_list


def get_sub_inventory_object(query_results, order_details):
    sub_inventory_record = SubInventory()
    sub_inventory_record.storeId = order_details[0]
    sub_inventory_record.productId = order_details[1]
    sub_inventory_record.orderId = order_details[2]
    sub_inventory_record.quantity = order_details[3]
    sub_inventory_record.discount = query_results.discount
    sub_inventory_record.price = query_results.price
    sub_inventory_record.delivery = 0

    return sub_inventory_record


def update_inventory(order_details_list):
    for order_details in order_details_list:
        query_results = db.session.query(Inventory).filter(Inventory.storeId == order_details[0]) \
            .filter(Inventory.productId == order_details[1]).first()
        query_results.quantity -= order_details[3]
        sub_inventory_record = get_sub_inventory_object(query_results, order_details)
        db.session.add(sub_inventory_record)
    db.session.commit()


if __name__ == "__main__":
    order_details_list = fetch_order_details(1)
    update_inventory(order_details_list)
