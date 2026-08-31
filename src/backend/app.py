from fastapi import FastAPI
from backend.controller.UserController import router as customer_router

app = FastAPI()
app.include_router(customer_router)
