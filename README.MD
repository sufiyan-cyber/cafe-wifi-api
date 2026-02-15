# Cafe & Wifi REST API ☕📡

A cloud-hosted RESTful API that provides information about cafes, including location, WiFi availability, seating, and coffee price.
The service allows users to search cafes, retrieve random suggestions, update pricing, and report closed cafes through authenticated requests.

This project demonstrates API development, database integration, deployment, and API documentation.

---

## 🔧 Tech Stack

* Python (Flask)
* Flask-SQLAlchemy ORM
* SQLite Database
* Gunicorn (production server)
* Render (cloud hosting)
* Postman (API documentation & testing)

---

## 🌐 Live API

Base URL:

https://cafe-wifi-api.onrender.com

---

## 📑 API Documentation

Interactive documentation (try requests directly in browser):

[Postman Documentation Link]

---

## 📌 Available Endpoints

### 1. Get all cafes

`GET /all`

Returns a list of all cafes stored in the database.

---

### 2. Search cafe by location

`GET /search?loc=<location>`

Example:
`/search?loc=London`

---

### 3. Get a random cafe

`GET /random`

Returns a random cafe recommendation.

---

### 4. Update coffee price

`PATCH /update-price/<id>?new_price=<price>`

Example:
`/update-price/3?new_price=3.5`

---

### 5. Report a cafe as closed 🔐

`DELETE /report-closed/<id>?api_key=<API_KEY>`

This endpoint is protected and requires an API key.

---

## 🔐 Authentication

Certain operations require an API key for security.

The server checks the key using environment variables (not hardcoded in the code).

---

## 🗄 Database

The project uses a SQLite database (`cafes.db`) containing cafe records such as:

* Name
* Location
* Maps link
* Image link
* Coffee price
* Seats available
* WiFi availability
* Power sockets availability

The database is preloaded with sample cafes for demonstration.

---

## 🚀 Deployment

The application is deployed using **Render** and runs with Gunicorn as the production WSGI server.

The server automatically:

* installs dependencies
* launches the Flask app
* exposes public endpoints

---

## ▶ Running Locally

1. Clone repository
2. Install dependencies

```
pip install -r requirements.txt
```

3. Run the server

```
python main.py
```

Then open:
http://127.0.0.1:5000

---

## 🎯 Project Purpose

This project was created to demonstrate:

* REST API design
* Database operations using ORM
* Secure endpoints with API key authentication
* Cloud deployment
* Professional API documentation

---

## 👤 Author

Sufiyan Khan S
Information Science & Engineering Student
Bangalore, India

---

## 📎 Links

Live API:
https://cafe-wifi-api.onrender.com

API Documentation:
https://documenter.getpostman.com/view/52395039/2sBXcBo3HV#intro
