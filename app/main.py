from fastapi import FastAPI
from routers import discrepancies
from config.settings import settings

app = FastAPI(title="Freight Discrepancy API")
app.include_router(discrepancies.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)