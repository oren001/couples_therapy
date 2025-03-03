import os
import sys
import webbrowser
import subprocess
import time

def check_dependencies():
    try:
        import flask
        import flask_cors
        import dotenv
        import openai
        return True
    except ImportError:
        return False

def install_dependencies():
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"])

def start_server():
    print("Starting server...")
    os.chdir("backend")
    subprocess.Popen([sys.executable, "server.py"])
    time.sleep(2)  # Wait for server to start

def open_interface():
    print("Opening interface in browser...")
    # Try to open the advanced interface first
    advanced_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "advanced-test.html")
    simple_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "simple-test.html")
    
    if os.path.exists(advanced_path):
        webbrowser.open(f"file://{advanced_path}")
    elif os.path.exists(simple_path):
        webbrowser.open(f"file://{simple_path}")
    else:
        print("Could not find interface files. Please check the frontend directory.")

def main():
    print("Welcome to Couples Therapy AI Assistant")
    
    if not check_dependencies():
        print("Missing dependencies detected.")
        response = input("Would you like to install them now? (y/n): ")
        if response.lower() == 'y':
            install_dependencies()
        else:
            print("Cannot continue without dependencies. Exiting...")
            return

    if not os.path.exists(os.path.join("backend", ".env")):
        print("\nWARNING: No .env file found in backend directory.")
        print("Please create one with your OpenAI API key before continuing.")
        print("See README.md for instructions.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return

    start_server()
    open_interface()
    
    print("\nServer is running at http://127.0.0.1:8000")
    print("Press Ctrl+C to stop the server when done.")

if __name__ == "__main__":
    main() 