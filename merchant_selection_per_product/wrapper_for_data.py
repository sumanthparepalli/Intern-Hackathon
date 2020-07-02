from app import app, db
from models import UserAddress, Inventory, Store, CreditScheme, Product
from merchant_selection_per_product import seller_ranking_from_product, distance_from_customer

"""
    This is a wrapper that converts the data from the db into lists for further processing.
    Seller Ranking for Product needs the following to work:
    1. inventory_list in form of list of lists where each list contains [storeId,productId,Quantity,Price,Discount]
    2. credit_scheme_available is a dictionary of sellers that have credit owned to the customer. 
    Key is storeId and value is 1 if the store owns some credit else it is 0
    3. customer_coordinate is a 1d list that contains [userId,latitude,longitude]
    4. store_coordinates  is a 2d list of stores that contains 
                [
                    [storeId,latitude,longitude],
                    [storeId,latitude,longitude]
                ]

    Input: An address_id and zip_code as Input
    Output: An inventory dictionary containing products with sellers sorted based on ranking score.
"""


def get_store_coordinates_list_from_zip_code(zip_code):
    query_result = db.session.query(Store.storeId, Store.latitude, Store.longitude).filter(
        Store.zipCode == zip_code).all()
    store_coordinates = []
    store_id_list = []
    for records in query_result:
        store_list = [records[0], float(records[1]), float(records[2])]
        store_id_list.append((records[0]))
        store_coordinates.append(store_list)
    return store_coordinates, store_id_list


def get_user_coordinate(address_id):
    query_result = db.session.query(UserAddress.userId, UserAddress.latitude, UserAddress.longitude).filter(
        UserAddress.addressId == address_id).all()
    user_coordinate = [query_result[0][0], float(query_result[0][1]), float(query_result[0][2])]
    return user_coordinate


def get_credit_scheme_dictionary(user_id, store_id_list):
    query_result = db.session.query(CreditScheme.storeId).filter(CreditScheme.userId == user_id).all()
    credit_scheme_available = {}
    for records in query_result:
        credit_scheme_available[records[0]] = 1

    for store_id in store_id_list:
        if store_id not in credit_scheme_available:
            credit_scheme_available[store_id] = 0

    return credit_scheme_available


def get_inventory_list(store_id_list):
    query_result = db.session.query(Inventory) \
        .filter(Inventory.storeId.in_(store_id_list)) \
        .filter(Inventory.quantity > 0).all()
    inventory_list = []
    for records in query_result:
        name = db.session.query(Product.productName).filter(Product.productId == records.productId).first()[0]
        inventory_record = [records.storeId, records.productId, float(records.price), records.quantity,
                            records.discount, name]
        inventory_list.append(inventory_record)

    return inventory_list


def input_for_wrapper(address_id, zip_code):
    store_coordinates, store_id_list = get_store_coordinates_list_from_zip_code(zip_code)
    user_coordinate = get_user_coordinate(address_id)
    credit_scheme_dict = get_credit_scheme_dictionary(user_coordinate[0], store_id_list)
    inventory_list = get_inventory_list(store_id_list)

    ######################################################
    distance_from_customer_dict = distance_from_customer.coordinate_input(user_coordinate, store_coordinates)
    inventory_dict = seller_ranking_from_product.convert_inventory_to_dict(inventory_list=inventory_list,
                                                                           credit_scheme_available=credit_scheme_dict,
                                                                           distance_from_customer=distance_from_customer_dict)
    inventory_dict = seller_ranking_from_product.sort_function(inventory_dict)
    return inventory_dict


if __name__ == "__main__":
    inventory_dict = input_for_wrapper(5, 522124)
    print(inventory_dict)
