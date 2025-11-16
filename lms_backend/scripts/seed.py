import asyncio
from src.db.mongodb import connect_to_mongo, close_mongo_connection, get_db
from src.services.auth_service import signup

async def main():
    await connect_to_mongo()
    db = get_db()
    try:
        # Seed an admin user if needed (password is placeholder, replace in real environments)
        try:
            uid = await signup(db, "admin@example.com", "ChangeMe123!", "Admin", "admin")
            print(f"Seeded admin user: {uid}")
        except ValueError:
            print("Admin user already exists.")
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())
