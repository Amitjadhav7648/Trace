from waitress import serve
from app import app

if __name__ == "__main__":
    print("Server Started on Port 5000...")
    serve(
        app,
        host="0.0.0.0",
        port=5000,
        threads=50
    )