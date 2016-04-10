from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Locations, Eats, Users
from flask import session as login_session

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
from wtforms import StringField, SubmitField, SelectMultipleField
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
    login_session['user_id'] = 'Guest'

# app error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

#JSON API endpoints
@app.route('/<int:loc_id>/JSON')
def JSONlocation(loc_id):
    return session.query(Locations).all().JSON_format()

@app.route('/<int:user_id>/JSON')
def JSONuser(user_id):
    locations_created = session.query(Locations).filter_by(user_id=user_id).all().JSON_format(),
    eat_created = session.query(Eats).filter_by(user_id=user_id).all().JSON_format()
    return locations_created, eats_created

@app.route('/<int:loc_id>/<int:eat_id>/JSON')
def JSONeat(loc_id, eat_id):
    return session.query(Eats).filter_by(loc_id=loc_id).filter_by(id=eat_id).filt.all().JSON_format()

#home page
@app.route('/test')
def test_base():
    return render_template('base.html')

@app.route('/')
@app.route('/home')
def home():
    recent_locations = session.query(Locations).order_by(Locations.id).limit(3)
    recent_eats = session.query(Eats).order_by(Eats.id).limit(3)
    return render_template('index.html', recent_eats=recent_eats,
                           recent_locations=recent_locations)

# TODO login methods

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state']= state
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
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
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    print '#### Acess Token %s' % login_session['access_token']
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

    # see if user exists, if it doesn't make a new one
    # user_id = getUserID(data["email"])
    # if not user_id:
    #     user_id = createUser(login_session)
    # login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route('/gdisconnect')
def gdisconnect():
    credentials = login_session.get('credentials')
    print credentials
    print login_session['access_token']
    if credentials is None:
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    result = httplib2.Http().request(url, 'GET')
    if result[0]['status'] == '200':
        # delete all stored variables in login_session
        del login_session['name']
        del login_session['email']
        del login_session['picture']
        del login_session['credentials']
        del login_session['access_token']
        del login_session['gplus_id']
        response = make_response(json.dumps('Successfully disconnected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

def fb_connect():
    return

def fb_disconnect():
    return


@app.route('/logout')
def disconnect():
    return

# HTML form helpers
class newLocationForm(Form):
    # TODO insert placeholder text for when this form used for editing existing items
    name = StringField('What is the name of the location?', validators = [Required()])
    description = StringField('Describe the location:')
    coordinates = StringField('What are the coordinates of the location?')
    pic_url = StringField('Add picture by URL:')
    submit = SubmitField('Submit')


class newEatForm(Form):
    name = StringField('What is the name of the steezyEat?', validators = [Required()])
    # TODO figure out proper syntax for select mulitple fields
    # category = SelectMultipleField('What is the category?', choices = ['greasy', 'snack', 'meat', 'fish', 'veggie'])
    description = StringField('Item description')
    pic_url = StringField('pic_url')
    location = StringField('loc_id')
    submit = SubmitField('Submit')


class newUserForm(Form):
    email = StringField("What is your Email?", validators = [Required()])

class deleteForm(Form):
    submit = SubmitField('Are you sure you want to delete?')

# CRUD methods

@app.route('/locations/')
def showAllLocs():
    locations = session.query(Locations).all()
    return render_template('locations.html', locations=locations)

@app.route('/locations/<int:loc_id>/')
def showOneLoc(loc_id):
    location = session.query(Locations).filter_by(id=loc_id).one()
    return render_template('onelocation.html', location=location)

# TODO add new Loc method
@app.route('/locations/new/', methods = ['GET', 'POST'])
def newLoc():
    form = newLocationForm()
    if request.method == 'POST' and form.validate_on_submit():
        n = Locations(name=form.name.data,
                     coordinates=form.coordinates.data,
                     description=form.description.data,
                     pic_url=form.pic_url.data)
        if login_session['user_id']:
            n.user_id = login_session['user_id']
        session.add(n)
        session.commit()
        flash('new location %s created!' % n.name)
        return redirect(url_for('showOneLoc', loc_id = n.id))
    else:
        return render_template('newlocation.html', form=form)

## TODO add location edit methods
@app.route('/locations/<int:loc_id>/edit/', methods = ['GET', 'POST'])
def editLoc(loc_id):
    # TODO check if user is user who can edit this locatio
    edited_location = session.query(Locations).filter_by(id=loc_id).one()
    # if login_session['user_id'] != edited_location.user_id:
    #     alert('You do not have permissions to edit this location.')
    #     return redirect(url_for('showOneLoc', loc_id=loc_id))
    form = newLocationForm()
    if request.method == 'POST' and form.validate_on_submit():
        if form.name.data:
            edited_location.name = form.name.data
        if form.coordinates.data:
            edited_location.coordinates=form.coordinates.data
        if form.description.data:
            edited_location.description=form.description.data
        if form.pic_url.data:
            edited_location.pic_url=form.pic_url.data
        session.add(edited_location)
        session.commit()
        flash('Location %s was edited!' % edited_location.name)
        return redirect(url_for('showOneLoc', loc_id = edited_location.id))
    else:
        return render_template('editlocation.html', form=form, location=edited_location)


@app.route('/locations/<int:loc_id>/delete', methods = ['GET', 'POST'])
def deleteLoc(loc_id):
    deleted_item = session.query(Locations).filter_by(id=loc_id).one()
    form = deleteForm()
    if request.method == 'POST':
        session.delete(deleted_item)
        session.commit()
        flash('Location %s deleted' % deleted_item.name)
        return redirect(url_for('showAllLocs'))
    else:
        return render_template('deletelocation.html', form=form, location=deleted_item.name)

# Eats CRUD methods

@app.route('/eats/')
def showAllEats():
    eats = session.query(Eats).all()
    return render_template('alleats.html', eats=eats)

@app.route('/eats/<int:eat_id>/')
def showOneEat(eat_id):
    return render_template('eat.html', eat_id=eat_id)

@app.route('/eats/new/', methods = ['GET', 'POST'])
def newEat(eat_id):
    form = newEatForm()
    if request.method == 'POST':
        n = Eats(name=request.form['name'],
                     user_id=login_session['user_id'],
                     description=request.form['description'],
                     pic_url=request.form['pic_url'],
                     loc_id=loc_id)
        session.add(n)
        session.commit()
        flash('new Eat %s created!' % n.name)
        new_loc_id = n.id
        return redirect(url_for('showEat', loc_id = n.id))
    else:
        return render_template('new_eat.html', form=form)


@app.route('/eats/<int:eat_id>/edit/')
def editEat(eat_id):
    # TODO check if user is user who can edit this locatio
    edited_eat = session.query(Eats).filter_by(id=eat_id).one()
    # if login_session['user_id'] != edited_location.user_id:
    #     alert('You do not have permissions to edit this location.')
    #     return redirect(url_for('showOneLoc', loc_id=loc_id))
    form = newEatForm()
    if request.method == 'POST' and form.validate_on_submit():
        if form.name.data:
            edited_location.name = form.name.data
        # if form.loc_id.data:
        #     edited_location.coordinates=form.coordinates.data
        if form.description.data:
            edited_location.description=form.description.data
        if form.pic_url.data:
            edited_location.pic_url=form.pic_url.data
        session.add(edited_eat)
        session.commit()
        flash('%s was edited!' % edited_eat.name)
        return redirect(url_for('showAllEats'))
    else:
        return render_template('editeat.html', eat=edited_eat, form=form)


@app.route('/eats/<int:eat_id>/delete/', methods=['GET', 'POST'])
def deleteEat(eat_id):
    eat=session.query(Eats).filter_by(id=eat_id).one()
    form=deleteForm()
    if request.method =='POST':
        session.delete(eat)
        session.commit()
        flash('You have deleted %s' % eat.name)
        return redirect(url_for('showAllEats'))
    return render_template('deleteitem.html', item=eat, form=form)

# User CRUD methods

@app.route('/users/<int:user_id>/')
def showProfile(user_id):
    return render_template('eat.html')

# TODO not sure if this needs to be placed somewhere else
@app.route('/users/new/')
def newUser():
    return render_template('eat.html')

@app.route('/users/<int:user_id>/edit/')
def editUser(loc_id, eat_id):
    return render_template('eat.html')

@app.route('/users/<int:user_id>/delete/')
def deleteUser(loc_id, eat_id):
    return render_template('eat.html')

if __name__ == '__main__':
    main()
