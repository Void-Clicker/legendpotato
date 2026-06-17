from supabase import create_client, Client

SUPABASE_URL = "https://your-project-ref.supabase.co"   # ← CHANGE THIS
SUPABASE_KEY = "your-anon-key-here"                     # ← CHANGE THIS (anon key is safe to use here)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
