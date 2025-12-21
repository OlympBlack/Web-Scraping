from services.supabase_client import supabase

res = supabase.table("quotes").select("*").limit(1).execute()
print(res)
