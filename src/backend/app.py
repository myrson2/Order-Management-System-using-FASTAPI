from fastapi import FastAPI
from backend.controller.CustomerController import router as customer_router
from backend.controller.MerchantController import router as merchant_router
from backend.controller.AuthenticationController import router as authentication_router

app = FastAPI()
app.include_router(customer_router)
app.include_router(merchant_router)
app.include_router(authentication_router)