from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists in the 'api' directory
load_dotenv()

app = Flask(__name__)

# --- CORS Configuration ---
# Allow requests from your Next.js development server (default port 3000)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})


# Database Configuration
# Using PostgreSQL 
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/postgres')

db = SQLAlchemy(app)

# API Routes
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify(message="Pong!")
    
# Main execution
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001) 