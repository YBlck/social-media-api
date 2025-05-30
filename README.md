# 📱 Social Media API

This is a RESTful API for a social media platform built with Django REST Framework. It supports user authentication, profile management, following system, post creation, and filtering.

## 🚀 Features

### 🔐 User Registration and Authentication

* Users can register using their email and password.

* Users can log in with their credentials and receive a JWT token.

* Token-based authentication using JWT (access & refresh tokens).

### 👤 User Profile

* Users can create and update their profile (including avatar, bio, country, and city).

* Users can retrieve their own profile and view other users’ profiles.

* Users can search for profiles by name, surname, country, and city.

### 🤝 Follow / Unfollow

* Users can follow and unfollow other users.

* Users can view the list of people they are following.

* Users can view their list of followers.

### 📝 Posts

* Users can create posts with text content and optional media attachments (images, videos, etc.).

* Users can retrieve their own posts.

* Users can view a feed of posts from profiles they follow.

* Users can filter posts by hashtag or title.

## ⚙️ Technologies Used

* Python 3.11 – core language

* Django 5.2 – backend web framework

* Django REST Framework – for building RESTful APIs

* SimpleJWT – for secure JWT-based authentication

* PostgreSQL – robust relational database used in production and development

* drf-spectacular – automatic OpenAPI schema generation and Swagger UI

## 🐳 Setup with Docker

### 1. Clone the repository

```
git clone https://github.com/YBlck/theater-rest-api.git
cd theater-rest-api
```

### 2. Create .env file
Use the provided .env.sample to create your own .env file:
```bash
cp .env.sample .env
```
Then fill in the values:
```
DJANGO_SECRET_KEY=<your-secret-key>
POSTGRES_DB=<your_db>
POSTGRES_USER=<your_user>
POSTGRES_PASSWORD=<your_password>
POSTGRES_HOST=db
POSTGRES_PORT=5432
```
### 3. Build and run the containers
```bash
docker-compose up --build
```
The API will be available at:
```
http://localhost:8000/
```
### 4. Create superuser
```bash
docker-compose exec theater python manage.py createsuperuser
```

## 📘 API Documentation (Swagger)
This project uses drf-spectacular to generate and serve OpenAPI-compliant documentation.

After starting the server, you can access the interactive API documentation at:

```
http://localhost:8000/api/doc/swagger/
```
You can also view the raw OpenAPI schema in JSON or YAML format:

```
http://localhost:8000/api/doc/
```

This documentation allows you to explore the endpoints, view request/response structures, and test API calls directly from the browser.


## 🧪 Running Tests

To run the tests with coverage, use the following commands:
```bash
docker-compose exec web coverage run manage.py test
```
To view the test coverage report:
```bash
docker-compose exec web coverage report
```