def convert_inventory_to_dict(inventory_list, credit_scheme_available, distance_from_customer):
    inventory_dict = {}
    for row in inventory_list:
        product_id = row[1]
        temp_row = row
        temp_row.pop(1)
        temp_row.append(credit_scheme_available[temp_row[0]])
        temp_row.append(distance_from_customer[temp_row[0]])
        if product_id in inventory_dict:
            inventory_dict[product_id].append(temp_row)
        else:
            inventory_dict[product_id] = [temp_row]
    return inventory_dict


def ranking_score(store_list):
    distance_score = 1.0 / store_list[-1]
    credit_score = 0
    if store_list[-2] == 1:
        credit_score = 1
    price_score = store_list[1] - ((store_list[1] * store_list[3]) / 100)
    price_score = 1.0/price_score
    final_ranking_score = .4 * distance_score + 0.2 * credit_score + .4 * price_score
    return -1.0 * final_ranking_score


def sort_function(inventory_dict):
    for productId in inventory_dict:
        store_array_with_product = inventory_dict[productId]
        store_array_with_product = sorted(store_array_with_product, key=ranking_score)
        inventory_dict[productId] = store_array_with_product
    return inventory_dict
