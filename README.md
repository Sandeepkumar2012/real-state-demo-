# Modern Real Estate Flask App

A responsive real estate web application built with Flask, Bootstrap 5, JavaScript, and SQLite via SQLAlchemy.

## Features

- Homepage with hero search and featured property cards
- Listings page with filters for city, property type, and price range
- Paginated property grid
- Property detail page with image gallery, amenities, and contact form
- Add Property admin-style form with image upload
- SQLite database with automatic sample data seeding

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Open the app at:

```text
http://127.0.0.1:5000
```

## Project Structure

```text
app.py
models.py
requirements.txt
templates/
  base.html
  index.html
  listings.html
  detail.html
  add.html
static/
  css/style.css
  js/main.js
  uploads/
```
