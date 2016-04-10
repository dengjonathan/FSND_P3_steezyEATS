# from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Locations, Users, Base, Eats, engine
from sqlalchemy import create_engine

engine = create_engine('sqlite:///steezyeats.db')
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

users = [
         {'name':'George Smith', 'email': 'gsmith@example.com', 'gplus_id': 'Gsmi','fb_id': 'GSmith', 'pic_url': 'http://stanlemmens.nl/wp/wp-content/uploads/2014/07/bill-gates-wealthiest-person.jpg'},
         {'name':'Patti Smith', 'email': 'psmith@example.com', 'gplus_id': 'PSmith', 'fb_id': 'PSmith', 'pic_url': 'http://stanlemmens.nl/wp/wp-content/uploads/2014/07/bill-gates-wealthiest-person.jpg'}
         ]

locations = [
                {'name': 'Burough Market', 'user_id': 1, 'coordinates': None, 'pic_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Borough_Market_cake_stall%2C_London%2C_England_-_Oct_2008.jpg/1024px-Borough_Market_cake_stall%2C_London%2C_England_-_Oct_2008.jpg?1459905269877'},
                {'name': 'Khaosan Road', 'user_id': 1, 'coordinates': None, 'pic_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Kohsan_Road_Bangkok.JPG/1024px-Kohsan_Road_Bangkok.JPG?1459905200852'},
                {'name': 'Khaosan Road', 'user_id': 1, 'coordinates': None, 'pic_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Kohsan_Road_Bangkok.JPG/1024px-Kohsan_Road_Bangkok.JPG?1459905200852'},
                {'name': 'Khaosan Road', 'user_id': 1, 'coordinates': None, 'pic_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Kohsan_Road_Bangkok.JPG/1024px-Kohsan_Road_Bangkok.JPG?1459905200852'},
                {'name': 'Khaosan Road', 'user_id': 1, 'coordinates': None, 'pic_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Kohsan_Road_Bangkok.JPG/1024px-Kohsan_Road_Bangkok.JPG?1459905200852'},
                {'name': 'Khaosan Road', 'user_id': 1, 'coordinates': None, 'pic_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Kohsan_Road_Bangkok.JPG/1024px-Kohsan_Road_Bangkok.JPG?1459905200852'},
            ]

eats = [
        {'name': 'Meat Pie', 'category': 'snack', 'user_id': 1,
         'loc_id': 1, 'description':'A meat pie is a pie with a filling of meat and often other savory ingredients.', 'pic_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Fatayer.jpg/1024px-Fatayer.jpg?1459905357379'},
        {'name': 'Veggie Scone', 'category': 'snack', 'user_id': 1, 'loc_id': 1, 'description': 'Deliciously savoury cheese scones, fortified by the inclusion of some fresh vegetables in the middle', 'pic_url': 'http://cdn.trendhunterstatic.com/thumbs/veggie-scone.jpeg'},
        {'name': 'Veggie Scone', 'category': 'snack', 'user_id': 1, 'loc_id': 1, 'description': 'Deliciously savoury cheese scones, fortified by the inclusion of some fresh vegetables in the middle', 'pic_url': 'http://cdn.trendhunterstatic.com/thumbs/veggie-scone.jpeg'},
        {'name': 'Veggie Scone', 'category': 'snack', 'user_id': 1, 'loc_id': 1, 'description': 'Deliciously savoury cheese scones, fortified by the inclusion of some fresh vegetables in the middle', 'pic_url': 'http://cdn.trendhunterstatic.com/thumbs/veggie-scone.jpeg'},
        {'name': 'Veggie Scone', 'category': 'snack', 'user_id': 1, 'loc_id': 1, 'description': 'Deliciously savoury cheese scones, fortified by the inclusion of some fresh vegetables in the middle', 'pic_url': 'http://cdn.trendhunterstatic.com/thumbs/veggie-scone.jpeg'},
        {'name': 'Veggie Scone', 'category': 'snack', 'user_id': 1, 'loc_id': 1, 'description': 'Deliciously savoury cheese scones, fortified by the inclusion of some fresh vegetables in the middle', 'pic_url': 'http://cdn.trendhunterstatic.com/thumbs/veggie-scone.jpeg'},
        {'name': 'Veggie Scone', 'category': 'snack', 'user_id': 1, 'loc_id': 1, 'description': 'Deliciously savoury cheese scones, fortified by the inclusion of some fresh vegetables in the middle', 'pic_url': 'http://cdn.trendhunterstatic.com/thumbs/veggie-scone.jpeg'}
       ]

def popUser(user):
    new = Users(name=user['name'],
                email=user['email'], gplus_id=user['gplus_id'],
                fb_id=user['fb_id'], pic_url=user['pic_url'])
    session.add(new)
    session.commit()
    print 'User %s added to db' % user['name']

def popLoc(location):
    new = Locations(name=location['name'], coordinates = location['coordinates'],
                    user_id=location['user_id'],
                    pic_url=location['pic_url'])
    session.add(new)
    session.commit()
    print 'Location %s added to db' % location['name']

def popEats(eat):
    new = Eats(name=eat['name'],
                description=eat['description'],
                category=eat['category'], pic_url=eat['pic_url'],
                user_id=eat['user_id'], loc_id=eat['loc_id']
              )
    session.add(new)
    session.commit()
    print 'Eat %s added to db' % new.name

def run():
    for user in users:
        popUser(user)
    for loc in locations:
        popLoc(loc)
    for eat in eats:
        popEats(eat)

run()
