import os
from supabase import create_client, Client

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_PUBLISHABLE_KEY")
supabase_service_key = os.environ.get("SUPABASE_SERVICE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL e SUPABASE_PUBLISHABLE_KEY precisam estar no .env")

# Cliente comum (para o dia a dia e login)
supabase: Client = create_client(supabase_url, supabase_key)

# Cliente Admin com superpoderes (para cadastrar usuários sem limitações)
if supabase_service_key:
    supabase_admin: Client = create_client(supabase_url, supabase_service_key)
else:
    supabase_admin = supabase