import json
import requests
import httplib2
import random
import string
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, asc
from flask import session as login_session
from database_setup import Base, Category, CategoryItem, User
from flask import Flask, render_template, redirect, request
from flask import url_for, jsonify, flash, make_response
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

app = Flask(__name__)

CLIENT_ID = json.loads(
  open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Recreational Warehouse"

# Connect to database
engine = create_engine('sqlite:///recreationalwarehouse.db', connect_args={'check_same_thread':False})
Base.metadata.bind = engine

# Create a database session
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create a state token
# Store token in a session for validation
@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase
                    + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect/', methods=['POST'])
def gconnect():

    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify the access token is used for intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
          json.dumps("Token's user ID doens't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
          json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps
                                 ('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserId(data['email'])
    if not user_id:
        user_id = createNewUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius:150px;\
               -webkit-border-radius: 150px; moz-border-radius:150px;">'
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


def getUserId(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    try:
        user = session.query(User).filter_by(id=user_id).one()
        return user
    except:
        return None


def createNewUser(login_session):
    newuser = User(name=login_session['username'], email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newuser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Disconnect user by revoking user's token and reset their login_session
@app.route('/gdisconnect/')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps
                                 ('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s'\
          % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        return redirect(url_for('showCategories'))


# Displays all of the categories
@app.route('/')
@app.route('/categories/')
def showCategories():
    categories = session.query(Category).all()
    if 'username' not in login_session:
        return render_template('publiccategories.html',
                               categories=categories)
    else:
        return render_template('categories.html', categories=categories)


# Creates a new category
@app.route('/categories/new/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['name']:
            category = Category(name=request.form['name'],
                                    user_id=login_session['user_id'])
            session.add(category)
            session.commit()
            flash('Category successfully created')
            return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html')


# Edits an existing category
@app.route('/categories/<int:category_id>/edit/',
           methods=['GET', 'POST'])
def editCategory(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if category.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized\
to edit this category. Please create your own category\
in order to edit.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            category.name = request.form['name']
            session.add(category)
            session.commit()
            flash('Category successfully edited')
            return redirect(url_for('showCategories'))
    else:
        return render_template('editCategory.html', category=category)


# Deletes an existing category
@app.route('/categories/<int:category_id>/delete/',
           methods=['GET', 'POST'])
def deleteCategory(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if category.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized\
to delete this category. Please create your own category\
in order to delete.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(category)
        session.commit()
        flash('Category successfully deleted')
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteCategory.html', category=category)


# Displays all items in the category
@app.route('/categories/<int:category_id>/items/')
def showItems(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(CategoryItem).\
        filter_by(category_id=category_id).all()
    creator = getUserInfo(category.user_id)
    if 'username' not in login_session or category.user_id != login_session['user_id']:
        return render_template('publiclist.html',
                               category=category, items=items, creator=creator)
    else:
        return render_template('list.html', category=category, items=items, creator=creator)


# Creates a new category item
@app.route('/categories/<int:category_id>/items/new/',
           methods=['GET', 'POST'])
def newCategoryItem(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if (request.form['name'], request.form['description']):
            categoryitem = CategoryItem(name=request.form['name'],
                                description=request.form['description'],
                                category=category,
                                user_id=category.user_id)
            session.add(categoryitem)
            session.commit()
            flash('Category item successfully created')
            return redirect(url_for('showItems', category_id=category.id))
    else:
        return render_template('newcategoryitem.html', category=category)


# Edits an existing category item
@app.route('/categories/<int:category_id>/items/<int:item_id>/edit/',
           methods=['GET', 'POST'])
def editCategoryItem(category_id, item_id):
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(CategoryItem).filter_by(id=item_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if category.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized\
to edit this category\'s item. Please create your own category item\
in order to edit.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if (request.form['name'], request.form['description']):
            item.name = request.form['name']
            item.description = request.form['description']
            item.category = category
            session.add(item)
            session.commit()
            flash('Category item successfully edited')
            return redirect(url_for('showItems', category_id=category.id))
    else:
        return render_template('editcategoryitem.html', category=category,
                               item=item)


# Deletes an existing category item
@app.route('/categories/<int:category_id>/items/<int:item_id>/delete/',
           methods=['GET', 'POST'])
def deleteCategoryItem(category_id, item_id):
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(CategoryItem).filter_by(id=item_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if category.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized\
to delete this category\'s item. Please create your own category item\
in order to delete.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash('Category item successfully deleted')
        return redirect(url_for('showItems', category_id=category.id))
    else:
        return render_template('deletecategoryitem.html', category=category,
                               item=item)


# JSON APIs to view category data
@app.route('/categories/JSON')
def categoryJSON():
    categories = session.query(Category).all()
    return jsonify(Categories=[category.serialize
                   for category in categories])


@app.route('/categories/<int:category_id>/items/JSON')
def categoryItemJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(CategoryItem).filter_by(category_id=category_id).all()
    return jsonify(CategoryItems=[item.serialize for item in items])


@app.route('/categories/<int:category_id>/items/<int:item_id>/JSON')
def menuItemJSON(category_id, item_id):
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(CategoryItem).filter_by(id=item_id).one()
    return jsonify(CategoryItem=[item.serialize])





if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.debug = True
    app.run(host='0.0.0.0', port=5050)
