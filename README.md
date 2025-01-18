# Payment Management Backend

This backend application is built using **FastAPI**, a modern Python web framework, to serve APIs for the payment management system.

## Requirements

Before running this project, ensure you have the following installed:

- **Python** (version 3.8 or higher)
- **pip** (Python package manager)
- **MongoDB** (local or cloud instance)

---

## Setting Up the Project

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Shahuljava/payment-management-backend.git
   cd payment-management-backend
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Linux/Mac
   venv\Scripts\activate     # For Windows
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**: Create a `.env` file in the project root and add the following:
   ```makefile
   MONGO_URI=<your-mongodb-uri>
   SECRET_KEY=<your-secret-key>
   ```

## Running the Application

- **Start the Server**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

- **Access the Application**:
   - API Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - ReDoc Documentation: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Project Structure

```
payment-management-backend/
├── main.py            # Application entry point
├── routes.py          # API routes
├── models.py          # Pydantic models for request validation
├── database.py        # MongoDB connection and utilities
├── .env               # Environment variables (not included in repo)
├── requirements.txt   # Python dependencies
└── README.md          # Project documentation
```

## API Endpoints

**Base URL**: `http://127.0.0.1:8000`

| Method | Endpoint               | Description                          |
|--------|-----------------------|--------------------------------------|
| GET    | /payments             | Get all payments                     |
| POST   | /payments             | Create a new payment                 |
| GET    | /payments/{payment_id}| Get details of a specific payment    |
| PUT    | /payments/{payment_id}| Update a specific payment            |
| DELETE | /payments/{payment_id}| Delete a payment                     |

## Testing the Application

- **Run Tests**: If you have unit tests, run them using:
   ```bash
   pytest
   ```

- **Testing APIs**: Use tools like Postman or cURL to test the API endpoints.

## Deployment

### Deploy to Heroku

1. **Create a Procfile**:
   ```plaintext
   web: uvicorn main:app --host=0.0.0.0 --port=${PORT}
   ```

2. **Install Gunicorn (Optional for Production)**:
   ```bash
   pip install gunicorn
   ```

3. **Commit and Push to Heroku**:
   ```bash
   git add .
   git commit -m "Prepare for Heroku deployment"
   git push heroku main
   ```

## Additional Notes

- Make sure to secure sensitive credentials (e.g., MONGO_URI and SECRET_KEY) using environment variables.
- For production, consider enabling HTTPS and using a cloud MongoDB service like MongoDB Atlas.
