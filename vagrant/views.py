from findARestaurant import findARestaurant
from models import Base, Restaurant
from flask import Flask, jsonify, request
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)




foursquare_client_id = '231PN4OL5FNNPEQU2ZLS5DZIYQFT14BZIGJFMANAVDQMT512'

foursquare_client_secret = 'LHX3DN4WCOFTBSU1MCTN3HAMVG4IBUWLPEURJY5CFSTYIWI0'

google_api_key = 'AIzaSyAy2WAiXdVqvtfo13WvzsWadWXlAmSE0Iw'

engine = create_engine('sqlite:///restaurants.db?check_same_thread=False')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

@app.route('/restaurants', methods = ['GET', 'POST'])
def all_restaurants_handler():
    if request.method == 'GET':
        restaurants = session.query(Restaurant).all()
        return jsonify(restaurants = [i.serialize for i in restaurants])

    elif request.method == 'POST':
        location = request.args.get('location', '')
        mealType = request.args.get('mealType', '')
        restaurant_info = findARestaurant(mealType, location)
#        prints fail to work due to ascii unicode error
#        print unicode(restaurant_info['name'])
#        print unicode(restaurant_info['address'])
#        print restaurant_info['image']
        if restaurant_info != 'No Restaurants Found':
            newRestaurant = Restaurant(restaurant_name = unicode(restaurant_info['name']), restaurant_address = unicode(restaurant_info['address']), restaurant_image = restaurant_info['image'])
            session.add(newRestaurant)
            session.commit()
            print 'New Restaurant added to database'
            return jsonify(newRestaurant = newRestaurant.serialize)
        else:
            return jsonify({"error":"No Restaurants Found for %s in %s" % (mealType, location)})

@app.route('/restaurants/<int:id>', methods = ['GET', 'PUT', 'DELETE'])
def restaurant_handler(id):
    restaurant = session.query(Restaurant).filter_by(id = id).one()
    if request.method == 'GET':
        return jsonify(restaurant = restaurant.serialize)

    elif request.method == 'PUT':
        if request.args.get('name', ''):
            restaurant.name = request.args.get('name', '')
        if request.args.get('address', ''):
            restaurant.address = request.args.get('address', '')
        if request.args.get('name', ''):
            restaurant.image = request.args.get('image', '')
        return jsonify(restaurant = restaurant.serialize)

    elif request.method == 'DELETE':
        session.delete(restaurant)
        session.commit()
        return "Restaurant Deleted"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
