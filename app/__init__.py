from flask import Flask 
import os 


def instantiate_application():

    app = Flask(__name__)

    # Load environment variables from .env file. 
    app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secretkey')

    # Import application page routes. 
    from app.Routes import main

    # Register that blueprint to access routes. 
    app.register_blueprint(main)
    
    # Return application.
    return app
    