from datetime import datetime
import json

class Shop:
    def __init__(self, name, latitude, longitude, address, products = []):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.products = products
        self.address = address
    def __json__(self):
        return {
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'products': self.products,
            'address': self.address.__json__()
        }
    for_json = __json__

class Address:
    def __init__(self, postal_code, street, house_number, city):
        self.postal_code = postal_code
        self.address = self.__build_address__(street, house_number)
        self.city = city
    def __build_address__(self, street = '', house_number = ''):
        if(type(street) == type(None)):
            street = ''
        return str(street) + ' ' + str(house_number)
    def __json__(self):
        return {
            'postalCode': self.postal_code,
            'address': self.address,
            'address2': '',
            'city': self.city,
            'district': '',
        }
    for_json = __json__

result = []
postal_codes = []
cities = []
start = datetime.now()
print('Started: ', start)
with open('export.geojson') as file:
    shop_data = json.load(file)
    
    for shop in shop_data['features']:
        
        try:
            shop_name = shop['properties']['name']
        except(KeyError):
            shop_name = ''

        shop_type = shop['geometry']['type']

        if (shop_type == 'Point'):
            shop_long = shop['geometry']['coordinates'][0]
            shop_lat = shop['geometry']['coordinates'][1]
        elif(shop_type == 'LineString'):
            shop_long = shop['geometry']['coordinates'][0][0]
            shop_lat = shop['geometry']['coordinates'][0][1]
        elif(shop_type == 'Polygon'):
            shop_long = shop['geometry']['coordinates'][0][0][0]
            shop_lat = shop['geometry']['coordinates'][0][1][1]
        elif(shop_type == 'MultiPolygon'):
            shop_long = shop['geometry']['coordinates'][0][0][0][0]
            shop_lat = shop['geometry']['coordinates'][0][0][0][1]
        else:
            print('Corrupt shop', shop_type)
            
        shop_address_postalcode = None
        shop_address_street = None
        shop_address_town = None
        shop_address_housenumber = None

        try:
            shop_address_postalcode = shop['properties']['addr:postcode']
            if(shop_address_postalcode not in postal_codes):
                postal_codes.append(shop_address_postalcode)
        except(KeyError):
            pass
        try:
            shop_address_street = shop['properties']['addr:street']
        except(KeyError):
            pass
        try:
            shop_address_town = shop['properties']['addr:city']
            if(shop_address_town not in cities):
                cities.append(shop_address_town)
        except(KeyError):
            pass
        try:
            shop_address_housenumber = shop['properties']['addr:housenumber']
        except(KeyError):
            pass
        sa = Address(
            shop_address_postalcode,
            shop_address_street,
            shop_address_housenumber,
            shop_address_town,
        )
        se = Shop(shop_name, shop_lat, shop_long, sa)
        
        result.append(se.__json__())
    
with open("./result.json", "w") as f:
    output = json.dumps(result, ensure_ascii=False)
    f.write(output)
    f.close()
end = datetime.now()
print('Ended: ', end)   
print('The task lasted: ', (end-start))
print(
    'In total this were ' + str(len(result)) + ' Shops to parse for our data.\n' +
    'The Shops are listed in: ' + str(len(postal_codes)) + ' postal codes.\n'
    'The Shops are listed in: ' + str(len(cities)) + ' cities.'

)

