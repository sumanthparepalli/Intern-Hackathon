"""
Receives a list of store with their id and coordinates(lat and lon) and customer coordinate
and returns the distance of stores coordinates from customers. The distance is appended in the original
store coordinate list and returned for further use.
"""
import requests


def convert_coordinate_to_string(coordinate):
    "coordinate is a list of 3 elements namely id, latitude and longitude"
    coordinate_string = '{' + '"latLng": {' + '"lat":' + str(coordinate[1]) + ',' + '"lng":' + str(coordinate[2]) + '}}'
    return coordinate_string


def generate_string_payload(customer_coordinate, store_coordinates):
    payload = '{' + '"locations"' + ': ['
    payload += convert_coordinate_to_string(customer_coordinate)
    for coordinate in store_coordinates:
        payload += ','
        payload += convert_coordinate_to_string(coordinate)
    payload += ']}'
    return payload


def get_distance_from_api(payload):
    base_url = 'http://www.mapquestapi.com/directions/v2/routematrix?key=7SfmHTLOkhRRcV7iPNPQC44AxpjxVEWe'
    response_from_api = requests.post(base_url, payload).json()
    print(response_from_api)
    return response_from_api["distance"]


def coordinate_input(customer_coordinate, store_coordinates):
    payload_string = generate_string_payload(customer_coordinate, store_coordinates)
    distance = get_distance_from_api(payload_string)
    distance_dict = {}
    distance.pop(0)
    j = 0
    for store_list in store_coordinates:
        storeId = store_list[0]
        distance_dict[storeId] = distance[j]
        j += 1
    return distance_dict
