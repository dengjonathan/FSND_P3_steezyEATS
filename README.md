FSND_P3_swiss_style

This package provides a Flask app that provides views from an SQLite database based on a Flask controller.

The website is SteezyEATS a food-based social networking site that allows users to authenticate with either Google Plus or Facebook,
and create, read, update, and delete street-food locations and things they've eaten.

This package has the following dependencies:
Flask (with flask-bootstrap and flask-wtf extensions)
SQLAlchemy
Oauth2client
httplib2
json
requests
wtforms

To run from the command line, unzip and cd into the directory then run the following commands:
  
    $ python database_setup.py
    $ python populate_database.py
    $ python steezyeats.py
    
This last command will serve the Flask app on the http address:
http://localhost:5001/

To change the port that the application is served on, modify main() in steezyeats.py

Acknowledgements:
This package was built as a Project 3 Submission for the Udacity Full Stack Developer Nanodegree
Additionally Miguel Grinberg's Flask tutorials and book "Flask Web Development" inspired some design patterns.
