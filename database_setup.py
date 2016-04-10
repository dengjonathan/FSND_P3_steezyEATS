from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250))
    gplus_id = Column(String(250))
    fb_id = Column(String(250))
    pic_url = Column(String(250))

    @property
    def JSON_format(self):
        """Formats user data into JSON readable format"""
        return {
            'name': self.name,
            'email': self.email,
            'id': self.id,
            'gplus_id': self.gplus_id,
            'fb_id': self.fb_id,
            'pic_url': self.pic_url
               }

class Locations(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    coordinates = Column(String(250))
    description = Column(String(1000))
    pic_url = Column(String(250))
    users = relationship(Users)

    @property
    def JSON_format(self):
        """Formats user data into JSON readable format"""
        return {
            'name': self.name,
            'coordinates': self.coordinates,
            'id': self.id,
            'user_id': self.user_id,
            'pic_url': self.pic_url
               }

# TODO for some reason Eats is saying there is not location_id
class Eats(Base):
    __tablename__ = 'eats'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(1000))
    category = Column(String(40))
    pic_url = Column(String(250))
    user_id = Column(Integer, ForeignKey('users.id'))
    loc_id = Column(Integer, ForeignKey('locations.id'))
    users = relationship(Users)
    locations = relationship(Locations)

    @property
    def JSON_format(self):
        """Formats user data into JSON readable format"""
        return {
            'name': self.name,
            'id': self.id,
            'user_id': self.user_id,
            'description': self.description,
            'category': self.category,
            'pic_url': self.pic_url,
            'loc_id' : self.loc_id
               }

engine = create_engine('sqlite:///steezyeats.db')
#create database engine
Base.metadata.create_all(engine)
#
# try:
#     execfile('populate_db.py')
#     print 'Database created and populated!!!'
# except:
#     print 'There was an error populating database'
