import sys, getopt
import json
from datetime import datetime
from pymodm.connection import connect
from pymongo.write_concern import WriteConcern
from pymodm import EmbeddedMongoModel, MongoModel, fields

class Product(MongoModel):
    name = fields.CharField()
    description = fields.CharField(blank=True)
    categories = fields.ListField(blank=True)
    createdAt = fields.DateTimeField()
    updatedAt = fields.DateTimeField(blank=True)

    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias = 'kuro'
        collection_name = 'products'

class Shop(MongoModel):
    name = fields.CharField(blank=True)
    location = fields.PointField(blank=True)
    products = fields.ListField(fields.ReferenceField(Product, blank=True))
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
    address2 = fields.CharField(blank=True)
    district = fields.CharField(blank=True)
    city = fields.CharField(blank=True)
    postalCode = fields.IntegerField(blank=True)

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

    start = datetime.now()
    print('Started: ', start)

    with open('./products.json', 'r') as f:
        products = json.load(f)

        ## Remove all Products in the database
        Product.objects.raw({}).delete()

        insertProducts = []
        for product in products:
            insertProducts.append(Product(
                product['name'], 
                product['description'],
                product['categories'],
                datetime.now(),
                datetime.now()
            ))

        Product.objects.bulk_create(insertProducts)

    with open('./result.json', 'r') as f:
        shops = json.load(f)
        ## Remove all Shops in the database
        Shop.objects.raw({}).delete()
        ## Remove all Addresses in the database
        Address.objects.raw({}).delete()

        insertAddresses = []
        for shop in shops:
            s = Shop(
                name = shop['name'], 
                location = {'type': 'Point', 'coordinates': [shop['latitude'], shop['longitude']]},
                products = Product.objects.all(),
                address = None,
                createdAt = datetime.now(),
                updatedAt = datetime.now()
            ).save()

            # Create the address for the shop
            address = shop['address']
            s.address = Address(
                shop = s, 
                address = address['address'], 
                address2 = address['address2'], 
                district = address['district'], 
                city = address['city'], 
                postalCode = address['postalCode']
                ).save()
            s.save()
    
    end = datetime.now()
    print('Ended: ', end)   
    print('The task lasted: ', (end-start))

if __name__ == "__main__":
   main(sys.argv[1:])
