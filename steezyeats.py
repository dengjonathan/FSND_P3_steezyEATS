from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Locations, Eats, Users
from flask import session as login_session
import time
from functools import wraps

# methods to create random state to prevent cross-site forgery attacks
import random
import string

# OAuth methods
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# flask extensions
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, SelectMultipleField, SelectField
from wtforms.validators import Required

app = Flask(__name__)
bootstrap = Bootstrap(app)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# SQLALCHEMY set up
engine = create_engine('sqlite:///steezyeats.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def main():
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5001)


# app error handlers
@app.errorhandler(404)
def page_not_found(e):
    """displays default template for 404 error"""

    return render_template('error.html', login_session=login_session), 404


# JSON API endpoints
# Below is a helpful debugging method that I created in development.  When
# the login/logout functions not working I could inspect the state of the
# session variables
@app.route('/login_session')
def showSession():
    list = []
    list.append([(i, login_session[i]) for i in login_session])
    return render_template('login_session.html', list=list)


@app.route('/locations/JSON')
def JSON_location():
    """returns attributes of all locations in JSON form"""

    locations = session.query(Locations).all()
    return jsonify(Locations=[i.JSON_format for i in locations])


@app.route('/locations/<int:loc_id>/JSON')
def JSON_one_location(loc_id):
    """returns attributes of one locations in JSON form"""

    location = session.query(Locations).filter_by(id=loc_id).one().name
    items = session.query(Eats).filter_by(loc_id=loc_id).all()
    return jsonify(eats=[i.JSON_format for i in items])


@app.route('/eats/JSON')
def JSON_eats():
    """returns attributes of all class Eats in JSON form"""

    items = session.query(Eats).all()
    return jsonify(eats=[i.JSON_format for i in items])

# home page


@app.route('/')
@app.route('/home')
def home():
    """displays view for homepage"""

    recent_locations = session.query(
        Locations).order_by(Locations.id.desc()).limit(4)
    recent_eats = session.query(Eats).order_by(Eats.id.desc()).limit(4)
    return render_template('index.html', recent_eats=recent_eats,
                           recent_locations=recent_locations,
                           login_session=login_session)


# helper methods
def createNewUser():
    """Creates a new user

    Creates a new object of the Users class and gives it attributes from
    user variables ins login_session
    """

    newUser = Users(name=login_session['username'],
                    pic_url=login_session['picture'],
                    email=login_session['email'],
                    )
    session.add(newUser)
    session.commit()
    return newUser.id


def getUserID(username):
    """Get a UserID given a username- a helper method for login/logout"""

    try:
        user = session.query(Users).filter_by(name=username).first()
        return user.id
    except:
        print 'no user stored under that username'
        return None


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in login_session:
            flash("Please login to create and edit items")
            return redirect(url_for('showLogin'))
        return f(*args, **kwargs)
    return decorated_function


# login/ logout methods
@app.route('/login')
def showLogin():
    """Returns view for login page"""

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state,
                           login_session=login_session)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
    Authenticate using Google Plus OAuth Method

    User will be prompted to login to Google Plus service and recieve a
    one-time-use code from the Google API.

    This code will be exchanged for an access_token from Google API allowing
    app to make server-side calls for the users name, profile picture and
    email address.
    """

    # Validate state token as CSRF protection
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
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
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
                json.dumps('Current user is already connected.'),
                200
                                )
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
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
    login_session['provider'] = 'google'

    # see if user exists in Users Table and add if doesn't exist
    if getUserID(login_session['username']) is not None:
        login_session['user_id'] = getUserID(login_session['username'])
    else:
        user_id = createNewUser()
        login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return redirect('home')


@app.route('/gdisconnect')
def gdisconnect():
    """disconnect from Google Plus login and delete Flask Session variables"""

    if not login_session['username']:
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    result = httplib2.Http().request(url, 'GET')
    if result[0]['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/fbconnect', methods=['POST'])
def fb_connect():
    """
    Authenticate using FB OAuth Authentication

    User will be prompted to login to Google Plus service and recieve a
    one-time-use code from the Google API.

    This code will be exchanged for an access_token from Google API allowing
    app to make server-side calls for the users name, profile picture and
    email address.
    """

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # TODO fb does not return access token here
    access_token = request.data
    print "access token received %s " % access_token

    # exhange one-time-use code for FB token
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type='
    url += 'fb_exchange_token&'
    url += 'client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly
    # logout, let's strip out the information before the equals sign in our
    # token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?'
    url += '%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists in Users Table and add if doesn't exist
    if getUserID(login_session['username']) is not None:
        login_session['user_id'] = getUserID(login_session['username'])
    else:
        user_id = createNewUser()
        login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect', methods=['GET', 'DELETE'])
def fb_disconnect():
    url = 'https://graph.facebook.com/%s/permissions' % login_session[
        'facebook_id']
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return 'You have logged out.'


@app.route('/logout')
def disconnect():
    """
    Calls appropriate logout function given provider stored in login_session
    context
    """

    if login_session['provider']:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
        if login_session['provider'] == 'facebook':
            fb_disconnect()
            del login_session['facebook_id']
        login_session['username'] = None
        # del login_session['user_id']
        del login_session['email']
        del login_session['picture']
        del login_session['access_token']
        del login_session['provider']
        del login_session['user_id']
        flash('You have been successfully logged out!')
    else:
        flash('You are currently not logged in!')
    return redirect(url_for('home'))


# WTForms classes for use in CRUD templates
class newLocationForm(Form):
    # TODO insert placeholder text for when this form used for editing
    # existing items
    name = StringField('What is the name of the location?',
                       validators=[Required()])
    description = StringField('Describe the location:')
    pic_url = StringField('Add picture by URL:')
    submit = SubmitField('Submit')


class newEatForm(Form):

    name = StringField('What is the name of the steezyEat?',
                       validators=[Required()])
    avail_categories = [('greasy', 'greasy'), ('snack', 'snack'),
                        ('meat', 'meat'), ('veggie', 'veggie'),
                        ('fish', 'fish')]
    category = SelectField('What is the category?', choices=avail_categories)
    description = StringField('Item description')
    pic_url = StringField('pic_url')
    location = SelectField('Location', choices=None)
    submit = SubmitField('Submit')


class newUserForm(Form):
    email = StringField("What is your Email?", validators=[Required()])


class deleteForm(Form):
    submit = SubmitField('Are you sure you want to delete?')

# Display Methods to display various views


@app.route('/locations/')
def showAllLocs():
    """Return view showing all locations"""

    locations = session.query(Locations).all()
    return render_template('locations.html',
                           locations=locations, login_session=login_session)


@app.route('/locations/<int:loc_id>/')
def showOneLoc(loc_id):
    """Return view showing one locations and all Eat objects associated"""

    location = session.query(Locations).filter_by(id=loc_id).one()
    eats = session.query(Eats).filter_by(loc_id=loc_id).all()
    return render_template('onelocation.html', location=location,
                           login_session=login_session, eats=eats)


@app.route('/eats/')
def showAllEats():
    """Returns a view showing all Eats objects"""

    eats = session.query(Eats).all()
    return render_template('alleats.html', eats=eats,
                           login_session=login_session)


# CRUD methods for class Locations
@app.route('/locations/new/', methods=['GET', 'POST'])
@login_required
def newLoc():
    """
    Creates new Location object

    Return form to create new Location object and stores result of form
    to database. Redirects to page for newly created object
    """

    form = newLocationForm()
    if request.method == 'POST' and form.validate_on_submit():
        n = Locations(name=form.name.data,
                      description=form.description.data,
                      pic_url=form.pic_url.data,
                      user_id=login_session['user_id'])
        session.add(n)
        session.commit()
        flash('new location %s created!' % n.name)
        return redirect(url_for('showOneLoc', loc_id=n.id))
    else:
        return render_template('newitem.html',
                               form=form, login_session=login_session)


@app.route('/locations/<int:loc_id>/edit/', methods=['GET', 'POST'])
@login_required
def editLoc(loc_id):
    """
    Return a form that allows user to edit attributes and modifies
    row in table Locations where id=loc_id
    """

    item = session.query(Locations).filter_by(id=loc_id).one()
    if login_session['user_id'] != item.user_id:
        flash("Sorry, you do not have permissions to edit this item")
        return redirect(url_for('showAllLocs'))
    form = newLocationForm()
    if request.method == 'POST' and form.validate_on_submit():
        if form.name.data:
            item.name = form.name.data
        if form.description.data:
            item.description = form.description.data
        if form.pic_url.data:
            item.pic_url = form.pic_url.data
        session.add(item)
        session.commit()
        flash('Location %s was edited!' % item.name)
        return redirect(url_for('showOneLoc', loc_id=item.id))
    else:
        return render_template('editlocation.html', form=form, location=item,
                               login_session=login_session)


@app.route('/locations/<int:loc_id>/delete', methods=['GET', 'POST'])
@login_required
def deleteLoc(loc_id):
    """
    Return a view asking to confirm deletion. If confirmed, deletes item
    from database.
    """
    deleted_item = session.query(Locations).filter_by(id=loc_id).one()
    if login_session['user_id'] != deleted_item.user_id:
        flash("Sorry, you do not have permissions to edit this item")
        return redirect(url_for('showAllLocs'))
    form = deleteForm()
    if request.method == 'POST':
        session.delete(deleted_item)
        session.commit()
        flash('Location %s deleted' % deleted_item.name)
        return redirect(url_for('showAllLocs'))
    else:
        return render_template('deletelocation.html', form=form,
                               location=deleted_item.name, item=deleted_item,
                               login_session=login_session)


# CRUD methods for class Eats

@app.route('/eats/new/', methods=['GET', 'POST'])
@login_required
def newEat():
    """
    Return a form allowing user to edit attributes of Eat object.
    If submitted, creates a new Eats object in database.
    """

    avail_locs = [(loc.id, loc.name) for loc in session.query(Locations).all()]
    form = newEatForm()
    form.location.choices = avail_locs
    if request.method == 'POST':
        n = Eats(name=form['name'].data,
                 description=form['description'].data,
                 pic_url=form['pic_url'].data,
                 loc_id=form['location'].data
                 )
        if login_session['username']:
            n.user_id = login_session['user_id']
        session.add(n)
        session.commit()
        flash('new Eat %s created!' % n.name)
        return redirect(url_for('showAllEats'))
    else:
        return render_template('newitem.html', item_name='Eat',
                               form=form, login_session=login_session)


@app.route('/eats/<int:eat_id>/edit/', methods=['GET', 'POST'])
@login_required
def editEat(eat_id):
    """
    Return a form allowing user to edit attributes of Eat object.
    If submitted, update object with id=eat_id in database.
    """
    edited_eat = session.query(Eats).filter_by(id=eat_id).one()
    if login_session['user_id'] != edited_eat.user_id:
        flash("Sorry, you do not have permissions to edit this item")
        return redirect(url_for('showAllEats'))
    form = newEatForm()
    avail_locs = [(loc.id, loc.name) for loc in session.query(Locations).all()]
    form.location.choices = avail_locs
    if request.method == 'POST':
        if form.name.data:
            edited_eat.name = form.name.data
        if form.description.data:
            edited_eat.description = form.description.data
        if form.pic_url.data:
            edited_eat.pic_url = form.pic_url.data
        if form.location.data:
            edited_eat.loc_id = form.location.data
        session.add(edited_eat)
        session.commit()
        flash('%s was edited!' % edited_eat.name)
        return redirect(url_for('showAllEats'))
    else:
        return render_template('editeat.html', eat=edited_eat,
                               form=form, login_session=login_session)


@app.route('/eats/<int:eat_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteEat(eat_id):
    """
    Return a view asking to confirm deletion. If confirmed, deletes item
    from database.
    """

    eat = session.query(Eats).filter_by(id=eat_id).one()
    if login_session['user_id'] != eat.user_id:
        flash("Sorry, you do not have permissions to edit this item")
        return redirect(url_for('showAllEats'))
    form = deleteForm()
    if request.method == 'POST':
        session.delete(eat)
        session.commit()
        flash('You have deleted %s' % eat.name)
        return redirect(url_for('showAllEats'))
    return render_template('deleteitem.html', item=eat, form=form,
                           login_session=login_session)


if __name__ == '__main__':
    main()
