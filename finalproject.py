from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

# ---- sqlalchemy and database setup ------
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()
# -------------------------------------------

#----- Temporary data for testing prior to DB setup -------------
# #Fake Restaurants
# restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}
# restaurants = [{'name': 'The CRUDdy Crab', 'id': '1'}, {'name':'Blue Burgers', 'id':'2'},{'name':'Taco Hut', 'id':'3'}]

# #Fake Menu Items
# #items = [ {'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'1'}, {'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'2'},{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3'},{'name':'Iced Tea', 'description':'with lemon','price':'$.99', 'course':'Beverage','id':'4'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'5'} ]
# items = {}
# item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree','id':'1'}
#--------------------------------------------------------------
# @app.after_request
# def add_header(r):
#     """
#     Add headers to both force latest IE rendering engine or Chrome Frame,
#     and also to cache the rendered page for 10 minutes.
#     """
#     r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     r.headers["Pragma"] = "no-cache"
#     r.headers["Expires"] = "0"
#     r.headers['Cache-Control'] = 'public, max-age=0'
#     return r

@app.route('/')
@app.route('/restaurants')
def showRestaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('allrestaurants.html', restaurants= restaurants)

@app.route('/restaurant/new', methods = ['POST','GET'])
def newRestaurant():
    if request.method == 'POST':
        if request.form['name']:
            new_r = Restaurant(name = request.form['name'])
            session.add(new_r)
            session.commit()
            flash("New Restaurant Added!")
            return redirect(url_for('showRestaurants'))
        else:
            error = "You must enter a name."
            return render_template('newrestaurant.html',error = error)
    else:
        return render_template('newrestaurant.html')

@app.route('/restaurant/<int:restaurant_id>/edit', methods = ['POST','GET'])
def editRestaurant(restaurant_id):
    r = session.query(Restaurant).filter_by(id= restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            r.name = request.form['name']
            session.add(r)
            session.commit()
            flash("Restaurant has been edited!")
            return redirect(url_for('showRestaurants'))
        else:
            error = "You must enter a name."
            return render_template('editrestaurant.html',restaurant = r, error = error)
    else:
        return render_template('editrestaurant.html',restaurant = r)

@app.route('/restaurant/<int:restaurant_id>/delete', methods = ['POST','GET'])
def deleteRestaurant(restaurant_id):
    #return 'Page for deleting restaurant {}'.format(restaurant_id)

#----- Add a line here that queries the DB for the restaurant ----------
    r = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method =='POST':
        session.delete(r)
        session.commit()
        flash("Restaurant Deleted!")
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('deleterestaurant.html',restaurant = r)


@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
    r = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
    return render_template('menu.html',restaurant = r, items = items)

@app.route('/restaurant/<int:restaurant_id>/menu/new', methods = ['POST','GET'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        if request.form['name']:
            item = MenuItem(name = request.form['name'], restaurant_id = restaurant_id)
            session.add(item)
            session.commit()
            flash("New Menu Item Added!")
            return redirect(url_for('showMenu',restaurant_id = restaurant_id))
        else:
            error = "You must have a name."
            return render_template('newmenuitem.html',restaurant_id = restaurant_id, error = error)
    else:
        return render_template('newmenuitem.html',restaurant_id = restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:item_id>/edit', methods= ['POST','GET'])
def editMenuItem(restaurant_id,item_id):
    #---- Add query for item to be edited ----------
    item = session.query(MenuItem).filter_by(id = item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
        if request.form['price']:
            item.price = request.form['price']
        if request.form['description']:
            item.description = request.form['description']
        session.add(item)
        session.commit()
        flash("Menu Item Edited!")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html',restaurant_id = restaurant_id,
                                item_id = item_id, item = item)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:item_id>/delete', methods= ['POST','GET'])
def deleteMenuItem(restaurant_id, item_id):
    #---- Add query for item to be deleted -----
    item = session.query(MenuItem).filter_by(id = item_id).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("Menu Item Deleted!")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deletemenuitem.html', restaurant_id = restaurant_id, item = item)

# API Endpoints
@app.route('/restaurants/JSON')
def restaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(Restaurants = [r.serialize for r in restaurants])

@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def menuJSON(restaurant_id):
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
    return jsonify(MenuItems = [i.serialize for i in items])

@app.route('/restaurant/<int:restaurant_id>/menu/<int:item_id>/JSON')
def itemJSON(restaurant_id,item_id):
    """
    This function checks that the item exists in the given menu.
    If it does, then it returns a JSON version of the menu item data.
    Otherwise, a JSON is returned with all fields set to 'None' ('null' when jsonified).

    """
    item = session.query(MenuItem).filter_by(id = item_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    item_ids = [i.id for i in items]
    if item_id in item_ids:
        return jsonify(MenuItem = item.serialize)
    return jsonify(MenuItem = {
            'name': None,
            'description': None,
            'id': None,
            'price': None,
            'course': None,
        })

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0',port = 5000)