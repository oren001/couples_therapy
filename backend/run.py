from flask_server import app

if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(debug=True, host="127.0.0.1", port=8000) 