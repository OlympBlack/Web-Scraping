import uuid
from services.supabase_client import supabase

try:
    res = supabase.table("quotes").insert({
    res = supabase.table("quotes").insert({
        "text": "Test quote",  
        "author": "Test Author", 
        "topic": "Testing",
        "link": "http://example.com",
        "image_url": "http://example.com/image.jpg"
    }).execute()
    print(res)
except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, 'json'):
        print(f"JSON: {e.json()}")
    if hasattr(e, 'message'):
        print(f"Message: {e.message}")
