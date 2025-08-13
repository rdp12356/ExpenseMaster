import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON = os.getenv("SUPABASE_ANON_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_ANON)

class AuthService:
    @staticmethod
    def sign_up(email: str, password: str, full_name: str):
        return supabase.auth.sign_up({
            "email": email, "password": password,
            "options": {"data": {"full_name": full_name}}
        })

    @staticmethod
    def sign_in(email: str, password: str):
        return supabase.auth.sign_in_with_password({"email": email, "password": password})

    @staticmethod
    def user():
        return supabase.auth.get_user()

    @staticmethod
    def sign_out():
        supabase.auth.sign_out()

class DbService:
    @staticmethod
    def ensure_profile(user_id, locale="en", base_currency="USD"):
        supabase.table("profiles").upsert({"id": user_id, "locale": locale, "base_currency": base_currency}).execute()

    @staticmethod
    def set_profile(user_id, **fields):
        return supabase.table("profiles").update(fields).eq("id", user_id).execute()

    @staticmethod
    def list_categories(user_id):
        return supabase.table("categories").select("*").eq("user_id", user_id).order("created_at").execute().data

    @staticmethod
    def add_category(user_id, name, icon="💸"):
        return supabase.table("categories").insert({"user_id": user_id, "name": name, "icon": icon}).execute().data[0]

    @staticmethod
    def add_expense(user_id, amount, currency, category_id=None, note=""):
        return supabase.table("expenses").insert({
            "user_id": user_id, "amount": amount, "currency": currency,
            "category_id": category_id, "note": note
        }).execute().data[0]

    @staticmethod
    def list_expenses(user_id, limit=100):
        return supabase.table("expenses").select("*, categories(name,icon)").eq("user_id", user_id)            .order("spent_at", desc=True).limit(limit).execute().data
