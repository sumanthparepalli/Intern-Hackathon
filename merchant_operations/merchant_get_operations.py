"""
A script to perform various database functions on merchant's side
"""
from app import db
from models import *



# Receives a user id and returns the list of storeId and store name owned by the user
def get_store_list(user_id):
    store_id_from_user = db.session.query(UserStoreMap.storeId).filter(UserStoreMap.userId ==  user_id).all()
    store_list = []
    for records in store_id_from_user:
        store_list.append(records.storeId)
    store_id_from_user = db.session.query(Store.storeId,Store.storeName).filter(Store.storeId.in_(store_list)).all()
    store_id_list = []
    for records in store_id_from_user:
        store_id_list.append({"storeId":records.storeId,"storeName":records.storeName})
    return store_id_list

#function to get store details based on storeid
def get_store_details(store_id):
    store_record= db.session.query(Store).filter(Store.storeId == store_id).first()
    store_information_list = {"storeId":store_record.storeId,
                              "storeName":store_record.storeName,
                              "country":store_record.country,
                              "productId": store_record.productId,
                              "state":store_record.state,
                              "city":store_record.city,
                              "zipCode":store_record.zipCode,
                              "latitude":float(store_record.latitude),
                              "longitude":float(store_record.longitude)}
    return store_information_list

#function to get inventory_details based on storeid
def get_inventory_details(store_id):
    inventory_record = db.session.query(Inventory).filter(Inventory.storeId == store_id).all()
    inventory_list = []
    for records in inventory_record:
        product_desc = db.session.query(Product.Description).filter(Product.productId == records.productId).first()
        inventory = {"storeId":records.storeId,
                     "productId":records.productId,
                     "productDesc":product_desc[0],
                     "price":float(records.price),
                     "quantity":records.quantity,
                     "discount":records.discount,}
        inventory_list.append(inventory)
    return inventory_list

#function to get Subinventory based on storeId:
def get_sub_inventory_details(store_id):
    sub_inventory_record = db.session.query(SubInventory).filter(SubInventory.storeId == store_id).filter(SubInventory.delivery == False).all()
    sub_inventory_list =[]
    for records in sub_inventory_record:
        productDesc = db.session.query(Product).filter(Product.productId == records.productId).first()
        sub_inventory = {"orderId":records.orderId,
                         "storeId":records.storeId,
                         "productId":records.productId,
                         "productDesc":productDesc.Description,
                         "price": float(records.price),
                         "quantity":records.quantity,
                         "discount":records.discount,
                         "delivery":records.delivery,
                         "paid":records.paid }
        sub_inventory_list.append(sub_inventory)
    return sub_inventory_list

def get_credit_scheme_details_based_on_merchant(merchant_id):
    store_id_list = get_store_list(merchant_id)
    credit_scheme_details_list = []
    for records in store_id_list:
        query_results = db.session.query(PrepaidScheme).filter(PrepaidScheme.storeId == records["storeId"]).first()
        credit_scheme_details = {
                                "storeId":query_results.storeId,
                                "storeName":records["storeName"],
                                "amount": float(query_results.amount),
                                "discount":query_results.discount
        }
        credit_scheme_details_list.append(credit_scheme_details)
    return credit_scheme_details_list

#function to get user id and amount , that the store owes credit to
def get_credit_scheme_details(store_id):
    user_detail_record = db.session.query(CreditScheme.userId,CreditScheme.amount,CreditScheme.discount).filter(CreditScheme.storeId == store_id).all()
    user_detail_list = []
    for records in user_detail_record:
        name = db.session.query(User.name).filter(User.id == records.userId).first()
        name = name[0]
        user_detail = {
                        "userId":records.userId,
                        "name": name,
                        "amount":float(records.amount),
                        "discount":records.discount}
        user_detail_list.append(user_detail)
    return user_detail_list

#function to get prepaid scheme store list
def get_prepaid_scheme_details(user_id):
    store_list = get_store_list(user_id=user_id)
    prepaid_scheme_details_list = []
    for records in store_list:
        query_results = db.session.query(PrepaidScheme).filter(PrepaidScheme.storeId == records["storeId"]).first()
        prepaid_scheme_details = {
                "storeId":records["storeId"],
                "storeName":records["storeName"],
                "amount": float(query_results.amount),
                "discount": query_results.discount
        }
        prepaid_scheme_details_list.append(prepaid_scheme_details)
    return prepaid_scheme_details_list

if __name__ == "__main__":
    print(get_prepaid_scheme_details(1))