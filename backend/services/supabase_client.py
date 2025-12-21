import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
# Prefer the Service Role Key for backend scripts to bypass RLS
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Supabase credentials are missing. Ensure SUPABASE_URL and SUPABASE_KEY (or SUPABASE_SERVICE_ROLE_KEY) are set.")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY 
)

def save_quote(quote_data: dict):
    """
    Inserts a quote into the 'quotes' table.
    """
    # Define valid columns for the table
    valid_columns = ["text", "author", "link", "image_url", "topic"]
    
    # Filter data to only include valid columns
    payload = {k: v for k, v in quote_data.items() if k in valid_columns}
    
    try:
        # Use upsert to handle potential duplicates if a unique constraint exists (e.g. on link or text)
        # on_conflict="link" or "text" depending on your schema. 
        # If no unique constraint, upsert works like insert for new ID.
        response = supabase.table("quotes").upsert(payload).execute()
        return response
    except Exception as e:
        print(f"Error saving quote: {e}")
        return None
