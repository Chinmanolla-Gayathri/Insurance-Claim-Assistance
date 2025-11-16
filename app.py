# app.py

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import os
from dotenv import load_dotenv # Used to load your .env file

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)

# --- 1. Database Configuration using Environment Variable ---
# Reads the connection string from your local .env file
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Optional: Add a secret key for security (also from .env)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key_if_missing')

db = SQLAlchemy(app)

# --- 2. Database Model: The Claim Table Structure ---
class Claim(db.Model):
    __tablename__ = 'claims'
    id = db.Column(db.Integer, primary_key=True)
    policy_number = db.Column(db.String(50), unique=True, nullable=False)
    date_of_incident = db.Column(db.Date, nullable=False)
    claim_type = db.Column(db.String(50), nullable=False)
    # New field to track status for the checklist feature later
    status = db.Column(db.String(50), default='Pending Review')

    def to_json(self):
        # A helper method to easily convert the Python object to JSON for the API response
        return {
            'id': self.id,
            'policy_number': self.policy_number,
            'date_of_incident': self.date_of_incident.isoformat() if self.date_of_incident else None,
            'claim_type': self.claim_type,
            'status': self.status
        }


# --- 3. API Endpoints (The Routes) ---

# Endpoint 1: Create a New Claim (The SAVE function for the OCR module)
@app.route('/claims', methods=['POST'])
def create_claim():
    try:
        data = request.get_json()

        # Simple Data Validation: Ensure all required fields are present
        required_fields = ['policy_number', 'date_of_incident', 'claim_type']
        if not data or not all(key in data for key in required_fields):
            return jsonify({"error": "Missing one or more required fields"}), 400

        # Attempt to convert the date string to a Python date object (CRITICAL for database)
        try:
            incident_date = date.fromisoformat(data['date_of_incident'])
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400


        new_claim = Claim(
            policy_number=data['policy_number'],
            date_of_incident=incident_date,
            claim_type=data['claim_type']
        )

        db.session.add(new_claim)
        db.session.commit()

        return jsonify(new_claim.to_json()), 201 # 201 means 'Created'

    except Exception as e:
        db.session.rollback()
        # Handle unique constraint violation (if policy_number already exists)
        if 'duplicate key value violates unique constraint' in str(e):
             return jsonify({"error": "A claim with this policy number already exists."}), 409
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


# Endpoint 2: Get All Claims (The READ function)
@app.route('/claims', methods=['GET'])
def get_claims():
    all_claims = Claim.query.all()
    return jsonify([claim.to_json() for claim in all_claims]), 200


# --- 4. Application Run Block ---
if __name__ == '__main__':
    # This block ensures the 'claims' table is created in your PostgreSQL database 
    # based on the Claim model when the app starts for the first time.
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)