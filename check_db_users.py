import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
from app import app
from database_engine import db

client = app.test_client()
res = client.get('/login')
html = res.get_data(as_text=True)

print("=== CHECKING RENDERED LOGIN HTML FOR SLIDER TOKEN ===")
for line in html.split('\n'):
    if 'challengeToken' in line or 'slider_token' in line:
        print(line)

print("\n=== TESTING LIVE POST TO /login WITH SLIDER TOKEN ===")
# Extract token from session
with client.session_transaction() as sess:
    tok = sess.get("slider_token")
    print("Session slider_token:", tok)

post_res = client.post("/login", data={
    "username": "admin",
    "password": "sana123",
    "slider_token": tok
}, follow_redirects=False)

print("POST Status Code:", post_res.status_code)
print("Redirect Location:", post_res.headers.get("Location"))
