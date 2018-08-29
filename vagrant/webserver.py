from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem
import re


engine = create_engine('sqlite:///restaurantmenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                restaurants = session.query(Restaurant).all()
                print restaurants
                for restaurant in restaurants:
                    output += restaurant.name
                    output += "<br><a href = '/restaurants/%s/edit'>Edit</a>" % restaurant.id
                    output += "<br><a href = '/restaurants/%s/delete'>Delete</a>" % restaurant.id
                    output += "<br>"
                    output += "<br>"
                output += "<a href = '/restaurants/new'>Make a New Restaurant Here</a><br><br>"
                output += "</body></html>"
                self.wfile.write(output)
#                print output
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'><h2>Make a New Restaurant</h2><input name='new_restaurant' type='text' placeholder = 'New Restaurant Name'><input type='submit' value='Create'></form>"
                output += "</body></html>"
                self.wfile.write(output)
#                print output
                return

            if self.path.endswith("/edit"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                restaurantID = re.search('/restaurants/(.*)/edit', str(self.path)).group(1)
#                restaurantID = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter(Restaurant.id == restaurantID).one()
                output = ""
                output += "<html><body>"
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'><h2>%s</h2><input name='new_name' type='text' placeholder = '%s'><input type='submit' value='Rename'></form>" % (restaurantID, restaurant.name, restaurant.name)
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    newinput = fields.get('new_restaurant')
                    print newinput
                    restaurant_new = Restaurant(name = newinput[0])
                    session.add(restaurant_new)
                    session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

                return

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    newinput = fields.get('new_name')
                    restaurantID = re.search('/restaurants/(.*)/edit', str(self.path)).group(1)
                    print newinput[0]
                    print restaurantID
                    restaurant = session.query(Restaurant).filter(Restaurant.id == restaurantID).one()
                    restaurant.name = newinput[0]
                    session.add(restaurant)
                    session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

                return

#            if self.path.endswith("/restaurants/new"):
#                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
#                if ctype == 'multipart/form-data':
#                    fields = cgi.parse_multipart(self.rfile, pdict)
#                    newinput = fields.get('new_restaurant')
#                    print newinput
#                    restaurant_new = Restaurant(name = newinput[0])
#                    session.add(restaurant_new)
#                    session.commit()
#
#                self.send_response(301)
#                self.send_header('Content-type', 'text/html')
#                self.send_header('Location', '/restaurants')
#                self.end_headers()

        except:
            pass

def main():
    try:
        port = 8080
        server = HTTPServer(('',port), webserverHandler)
        print "Web server running on port %s" % port
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        server.socket.close()

if __name__ == '__main__':
    main()
