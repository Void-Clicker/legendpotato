from supabase import create_client, Client

SUPABASE_URL = "https://gzcbnuxuraoavywfouhg.supabase.co"   # ← CHANGE THIS
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6Y2JudXh1cmFvYXZ5d2ZvdWhnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE3MTA0NTUsImV4cCI6MjA5NzI4NjQ1NX0.kkg9kL7jq4EzIap4i0OFkLdqQPG-geyObe_Evd-cFVk"                     # ← CHANGE THIS (anon key is safe to use here)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
