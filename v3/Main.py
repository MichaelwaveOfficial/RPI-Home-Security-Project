from app import instantiate_application
import os

def main():
    
    # Create an instance of the application. 
    app = instantiate_application()

    # Run server with set variables. 
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=os.getenv('DEBUG', 'TRUE')
    )


if __name__ == '__main__':
    main()
