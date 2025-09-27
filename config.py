import os

class Config:
    SECRET_KEY = "super-secret-key"
    
    # MongoDB URI (replace with your credentials)
    # Format: mongodb://username:password@host:port/database
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/local_service_marketplace")
    
    # Optional: default database name
    MONGO_DBNAME = os.getenv("MONGO_DBNAME", "local_service_marketplace")
