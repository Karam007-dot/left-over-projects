# Finio — Local Setup

## Requirements
- Python 3.9+

## Install dependencies
```
pip install -r requirements.txt
```

## Run migrations
```
python manage.py migrate
```

## Start the server
```
python manage.py runserver
```

Then open http://127.0.0.1:8000 in your browser.

## Optional: Plaid bank connection
Create a `.env` file in this folder with your Plaid sandbox keys:
```
PLAID_CLIENT_ID=your_client_id
PLAID_SECRET=your_secret_key
PLAID_ENV=sandbox
```
Get keys at https://dashboard.plaid.com — use sandbox credentials `user_good` / `pass_good` to test.
