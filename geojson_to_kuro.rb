#!/usr/bin/env jruby
require 'json'

result = []

class Shopentry
    def initialize(name, lon, lat, addr)
        @name = name
        @latitude = lat
        @longitude = lon
        @products = []
        @address = addr
    end

    def to_s
        s = StringIO.new
        s << @name
        s << " "
        s << @latitude
        s << " "
        s << @longitude
        s << " "
        s << @address

        s.string
    end

    def to_hash
        {
            name: @name,
            latitude: @latitude,
            longitude: @longitude,
            products: [],
            address: @address
        }
        end

    def to_json(options = {})
        to_hash.to_json
    end
end

class Address
    def initialize(postalCode, street, town, housenumber)
        s = StringIO.new
        s << street
        s << " "
        s << housenumber
        @postalCode = postalCode
        @address = s.string
        @address2 = ""
        @district = ""
        @city = town
    end

    def to_s
        s = StringIO.new
        s << @address
        s << " "
        s << @city
        
        s.string
    end

    def to_hash
        {
            postalCode: @postalCode,
            address: @address,
            address2: "",
            district: "",
            city: @city
        }
    end
    
    def to_json(options = {})
        to_hash.to_json
    end
end

t1 = Time.now
puts "Started at: " << t1.to_s

file = File.open("./export.geojson")
file_data = file.read

json_data = JSON.parse(file_data)

for obj in json_data['features'] do
    
    shop_name = obj['properties']['name']

    if(shop_name == nil) 
        next;
    end

    shop_lat = nil
    shop_lon = nil

    case obj['geometry']['type']
    when "Point"
        shop_lat = obj['geometry']['coordinates'][0]
        shop_lon = obj['geometry']['coordinates'][1]
    when "LineString"
        shop_lat = obj['geometry']['coordinates'][0][0]
        shop_lon = obj['geometry']['coordinates'][0][1]
    when "Polygon"
        shop_lat = obj['geometry']['coordinates'][0][0][0]
        shop_lon = obj['geometry']['coordinates'][0][0][1]
    when "MultiPolygon"
        shop_lat = obj['geometry']['coordinates'][0][0][0][0]
        shop_lon = obj['geometry']['coordinates'][0][0][0][1]
    end 

    shop_address_postalcode = obj['properties']['addr:postcode']
    shop_address_street = obj['properties']['addr:street']
    shop_address_town = obj['properties']['addr:city']
    shop_address_housenumber = obj['properties']['addr:housenumber']

    sa = Address.new(shop_address_postalcode, shop_address_street, shop_address_town, shop_address_housenumber)
    se = Shopentry.new(shop_name, shop_lat, shop_lon, sa)

    result << se;
end

f = File.new("./result.json", "w")
str = JSON.dump(result)
f.write(str)
f.close
t2 = Time.now
puts "Ended at: " << t2.to_s
puts "It took summa sumarum: " << (t2-t1).to_s << " ms."