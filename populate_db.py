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
         {'name':'George Smith', 'email': 'gsmith@example.com', 'pic_url': 'http://stanlemmens.nl/wp/wp-content/uploads/2014/07/bill-gates-wealthiest-person.jpg'},
         {'name':'Patti Smith', 'email': 'psmith@example.com', 'pic_url': 'http://stanlemmens.nl/wp/wp-content/uploads/2014/07/bill-gates-wealthiest-person.jpg'}
         ]

locations = [
                {'name': 'Borough Market', 'user_id': 1, 'description':'London\'s oldest market dating back to the thirteenth century is also the busiest, and the most popular for gourmet goodies. If food is your thing, then Borough is the place to go.', 'pic_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Borough_Market_cake_stall%2C_London%2C_England_-_Oct_2008.jpg/1024px-Borough_Market_cake_stall%2C_London%2C_England_-_Oct_2008.jpg?1459905269877'},
                {'name': 'Khaosan Road', 'user_id': 1, 'description':'Hippie Heaven. Really needs no description.','pic_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Kohsan_Road_Bangkok.JPG/1024px-Kohsan_Road_Bangkok.JPG?1459905200852'},
                {'name': 'Hawker House', 'user_id': 1,  'description': 'Street food fiends can keep eating through the winter months thanks to this huge indoor night market.','pic_url': 'https://media.timeout.com/images/101224701/617/347/image.jpg'},
                {'name': 'Berwick Street Market', 'user_id': 1, 'description':'Situated on the stretch of Berwick Street between the Soho strip joints of Walker\'s Court and the elegant Yauatcha restaurant, this fruit and veg market is one of London\'s oldest.','pic_url': 'https://media.timeout.com/images/100685745/617/347/image.jpg'},
                {'name': 'Broadway Market', 'user_id': 1, 'description':'For east London\'s fashionably attired food-lovers, there\'s no better Saturday destination than Broadway Market.','pic_url': 'http://www.christopherfowler.co.uk/blog/wp-content/uploads/2011/03/broadway.jpg'},
                {'name': 'Brixton Market', 'user_id': 1, 'description': 'Brixton Market is a sensory fiesta. And for every hipster rammed into one of the (justifiably) rave reviewed eateries a stack of exotic produce still teeters like a nutritious Jenga set.','pic_url': 'https://media.timeout.com/images/100685217/185/139/image.jpg'},
            ]

eats = [
        {'name': 'Meat Pie', 'category': 'snack', 'user_id': 1,
         'loc_id': 1, 'description':'A meat pie is a pie with a filling of meat and often other savory ingredients.', 'pic_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Fatayer.jpg/1024px-Fatayer.jpg?1459905357379'},
        {'name': 'Veggie Scone', 'category': 'snack', 'user_id': 1, 'loc_id': 1, 'description': 'Deliciously savoury cheese scones, fortified by the inclusion of some fresh vegetables in the middle', 'pic_url': 'http://www.sugardishme.com/wp-content/uploads/2014/01/Garden-Veggie-Scones-1.jpg'},
        {'name': 'Empanadas', 'category': 'snack', 'user_id': 1, 'loc_id': 2, 'description': 'Although empanadas (stuffed pastries, usually savory) can be found throughout Argentina, the best ones are from the Salta region in the northwestern part of the country. It is also the only region where hot sauce is common. Hurrah!!', 'pic_url': 'http://photos.uncorneredmarket.com/South-America/Argentina/Argentina-Food/i-vzpQRcq/1/730x485/Argentina_Empanada-2-730x485.jpg'},
        {'name': 'Kebabs', 'category': 'snack', 'user_id': 1, 'loc_id': 3, 'description':'Although kebabs, grilled ground or chunked meat on a skewer, are not unique to Armenia, we did find that when we wanted a quick and easy snack, a kebab wrapped in lavash (flat bread) was the street food of choice', 'pic_url': 'http://photos.uncorneredmarket.com/Caucasus/Armenia/Armenian-Food-Markets/i-T35LSTz/1/730x485/Armenia_kebabs-2-730x485.jpg'},
        {'name': 'Singara', 'category': 'snack', 'user_id': 1, 'loc_id': 3, 'description':'Singara are spiced potato and vegetable mixture pockets wrapped in a thin dough and fried. What distinguishes a good singara is how flaky the texture is. Some are so flaky, as if they\'re made with savory pie crust. Singara are ubiquitous and inexpensive (as cheap as 24 for $1).', 'pic_url': 'http://photos.uncorneredmarket.com/Asia/Bangladesh/Srimongal-Tea-Gardens/i-DNBDVJX/0/730x485/5924102278_1e3be082ab_o-730x485.jpg'},
        {'name': 'Nasi campur', 'category': 'snack', 'user_id': 1, 'loc_id': 4, 'description': 'Nasi campur is essentially a Balinese mixed plate served with rice. Most restaurants will make the choice for you, but at warungs, the more local food outlets on Bali, the nasi campur selection is up to you. You can choose from delectables such as sate lilit, spicy tempeh, chopped vegetables, spice-rubbed meat, chicken, and tofu.', 'pic_url': 'http://photos.uncorneredmarket.com/Asia/Bali/Bali-Food/i-rBphZns/1/730x548/Bali_food-2-730x548.jpg'},
        {'name': 'Dumplings', 'category': 'snack', 'user_id': 1, 'loc_id': 1, 'description': 'These pork, shrimp and leek dumplings at Da Yu dumpling joint near the No.6 bathing area in Qingdao stick out. Fresh, delicious and perfectly steamed.', 'pic_url': 'http://photos.uncorneredmarket.com/Asia/China/Qingdao-Shanghai/i-LHzNQLZ/0/730x548/2125277005_2ba46077c8_o-730x548.jpg'}
       ]

def popUser(user):
    new = Users(name=user['name'],
                email=user['email'],
                pic_url=user['pic_url'])
    session.add(new)
    session.commit()
    print 'User %s added to db' % user['name']

def popLoc(location):
    new = Locations(name=location['name'],
                    user_id=location['user_id'],
                    description = location['description'],
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
