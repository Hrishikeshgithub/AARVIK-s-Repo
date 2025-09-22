import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

async def test_mongo_connection():
    load_dotenv()
    mongo_url = os.getenv("MONGO_URL")
    db_name = os.getenv("DB_NAME")
    
    if not mongo_url or not db_name:
        print("Error: MONGO_URL or DB_NAME not set in .env")
        return
    
    try:
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        result = await db.command('ping')
        print(f"Connection successful: {result}")
    except Exception as e:
        print(f"Connection failed: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_mongo_connection())