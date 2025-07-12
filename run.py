# run.py
import uvicorn
import os

ENV = os.getenv("ENVIRONMENT", "development")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=(ENV == "development")
    )
