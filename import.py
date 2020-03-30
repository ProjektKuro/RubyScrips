import sys, getopt
import json
from datetime import datetime
from pymodm.connection import connect
from pymongo.write_concern import WriteConcern
from pymodm import EmbeddedMongoModel, MongoModel, fields

class Product(EmbeddedMongoModel):
    name = fields.CharField()
    description = fields.CharField(blank=True)
    categories = fields.ListField(blank=True)
    quantity = fields.IntegerField(blank=True)
    createdAt = fields.DateTimeField()
    updatedAt = fields.DateTimeField(blank=True)

    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias = 'kuro'
        collection_name = 'products'

class Shop(MongoModel):
    name = fields.CharField(blank=True)
    location = fields.PointField(blank=True)
    products = fields.EmbeddedDocumentListField(Product, blank=True)
    address = fields.ReferenceField('Address', blank=True)
    createdAt = fields.DateTimeField()
    updatedAt = fields.DateTimeField(blank=True)

    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias = 'kuro'
        collection_name = 'shops'

class Address(MongoModel):
    shop = fields.ReferenceField(Shop, blank=True)
    address = fields.CharField()
    city = fields.CharField(blank=True)
    postCode = fields.IntegerField(blank=True)

    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias = 'kuro'
        collection_name = 'addresses'

def main(argv):
    user = ''
    password = ''
    try:
        opts, args = getopt.getopt(argv,"hu:p:",["user=","password="])
    except getopt.GetoptError:
        print("import.py -u <user> -p <password>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("import.py -u <user> -p <password>")
            sys.exit()
        elif opt in ("-u", "--user"):
            user = arg
        elif opt in ("-p", "--password"):
            password = arg
   
    if(user == '' or password == ''):
        print("username or password not provided")
        sys.exit()

    # Connect to MongoDB and call the connection "kuro".
    connect("mongodb://"+user+":"+password+"@37.120.164.78:27017/kuro", alias="kuro")

    post_codes = []
    cities = []
    insertProducts = []
    start = datetime.now()
    print('Started: ', start)

    # Create all products
    with open('./products.json', 'r') as f:
        products = json.load(f)

        ## Remove all Products in the database
        # Product.objects.raw({}).delete()

        for product in products:
            insertProducts.append(Product(
                name = product['name'], 
                description = product['description'],
                categories = product['categories'],
                quantity = 100,
                createdAt = datetime.now(),
                updatedAt = datetime.now()
            ))

        # Product.objects.bulk_create(insertProducts)

    with open('result.json') as file:
        shop_data = json.load(file)
        ## Remove all Shops in the database
        Shop.objects.raw({}).delete()
        ## Remove all Addresses in the database
        Address.objects.raw({}).delete()
        
        for shop_json in shop_data:
            
            ############
            ## Shops
            ############

            # get the shops name
            try:
                shop_name = shop_json['name']
            except(KeyError):
                # skip if none exists
                continue

            # get the geolocation of a shop
            # try:
            #     shop_location = {'type': 'Point', 'coordinates': [shop_json['latitude'], shop_json['longitude']]},
            # except(KeyError):
            #     # skip if none exists
            #     continue

            # assign all products to a shop
            # shop_products = Product.objects.all(),

            # assign empty address to shop
            shop_address = None

            ### Create shop object
            shop = Shop(
                name = shop_name, 
                location = {'type': 'Point', 'coordinates': [shop_json['latitude'], shop_json['longitude']]},
                products = insertProducts,
                address = shop_address,
                createdAt = datetime.now(),
                updatedAt = datetime.now()
            ).save()

            ############
            ## Addresses
            ############

            address_json = shop_json['address']
            # get the address street name
            try:
                shop_address_street = address_json['address']
            except(KeyError):
                pass

            # get the address post code
            try:
                shop_address_postcode = address_json['postalCode']
                if(shop_address_postcode not in post_codes):
                    post_codes.append(shop_address_postcode)
            except(KeyError):
                pass

            # get the address city
            try:
                shop_address_town = address_json['city']
                if(shop_address_town not in cities):
                    cities.append(shop_address_town)
            except(KeyError):
                pass

            # Create the address object while simultaneously setting the shop to the last created and updating the shops address
            shop.address = Address(
                shop = shop, 
                address = shop_address_street,
                city = shop_address_town, 
                postCode = shop_address_postcode
                ).save()
            shop.save()

            break
    
    end = datetime.now()
    print('Ended: ', end)   
    print('The task lasted: ', (end-start))
    print(
        'In total there were ' + str(Shop.objects.raw({}).count()) + ' Shops to parse from our data.\n' +
        'The Shops are listed in: ' + str(len(post_codes)) + ' postal codes.\n'
        'The Shops are listed in: ' + str(len(cities)) + ' cities.'
    )

if __name__ == "__main__":
   main(sys.argv[1:])
