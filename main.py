import os
from flask import Flask
from application import config
from application.config import LocalDevelopmentConfig
from application.database import db


app = None

def create_app():
    app = Flask(__name__, template_folder="templates")
    if os.getenv('ENV',"development") == "production":
        raise Exception("Currently no production Config is setup")

    else:
        print("Starting Local Development")
        app.config.from_object(LocalDevelopmentConfig)
    app.config['SECRET_KEY'] = 'Password@123'  # Replace 'your_secret_key' with a random and secret key

    db.init_app(app)
    app.app_context().push()
    return app

app = create_app()

# Import all the controllers once they are loaded!

from application.controllers import *

if __name__ == '__main__':
    # Run the flask app
    db.create_all()
    app.run(host='0.0.0.0', port=8001)


