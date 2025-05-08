from app import build_app
import os

def main():
    
    # Create an instance of the application. 
    app = build_app()

    # Run server with set variables. 
    app.run(
        host=os.getenv('HOST'),
        port=os.getenv('PORT'),
        debug=os.getenv('DEBUG')
    )


if __name__ == '__main__':
    main()