import sys
import os

# Add your project directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import app

# This is the callable that the server expects
application = app

if __name__ == "__main__":
    application.run()