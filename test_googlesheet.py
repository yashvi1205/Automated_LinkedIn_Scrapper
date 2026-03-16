# test_google.py
from google_sheets import save_to_sheet

save_to_sheet(
    user="Test User",
    url="https://linkedin.com/in/test",
    post="Post",
    text="Hello world",
    likes=0,
    comments=0,
    reposts=0
)