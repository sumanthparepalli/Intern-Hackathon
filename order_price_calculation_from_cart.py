"""
This script is used to calculate the order price based on the discounts and credit scheme table.
"""
from app import app, db
from models import Inventory, CreditScheme


# Takes a cart and calculates the price based on discount, merchant and credit scheme

def get_credit_scheme_details(user_id, store_id):
    credit_scheme_records = db.session.query(CreditScheme).filter(CreditScheme.userId == user_id).filter(
        CreditScheme.storeId == store_id).first()
    if credit_scheme_records == None:
        return -1
    credit_scheme_details_list = []
    credit_scheme_details_list = [credit_scheme_records.userId, credit_scheme_records.storeId,
                                  credit_scheme_records.amount, float(credit_scheme_records.discount)]
    return credit_scheme_details_list


def calculate_price_with_discount(quantity, price, discount):
    selling_price = quantity * (price - (price * discount) / 100)
    return selling_price


def cart_input(cart):
    # items is a list items = [userId,storeId,productId,quantity]
    for items in cart:
        inventory_record = db.session.query(Inventory).filter(Inventory.storeId == items[1]).filter(
            Inventory.productId == items[2]) \
            .filter(Inventory.quantity >= items[3]).first()
        if inventory_record == None:
            items.append(-1)
            items.append("Quantity exceeds the available amount")
        else:
            credit_scheme_details = get_credit_scheme_details(items[0], items[1])
            discount = inventory_record.discount
            if (credit_scheme_details != -1):
                discount += credit_scheme_details[3]
            selling_price = calculate_price_with_discount(items[3], float(inventory_record.price), discount)
            items.append(selling_price)
            items.append("Quantity available as requested")
    return cart


if __name__ == "__main__":
    cart = [[2,1,1,2],[2,2,2,3],[2,3,5,2],[2,4,4,1],[2,3,1,1000]]
    cart = cart_input(cart)
    for items in cart:
        print(items)