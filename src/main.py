from fastapi import FastAPI
from src.expenses.router import router as expenses_router
from src.auth.router import router as auth_router 
from src.exceptions import setup_exception_handlers
from src.auth.router import admin_router
from src.middleware import LoggingMiddleware

app = FastAPI()

app.include_router(expenses_router)
app.include_router(auth_router)
app.include_router(admin_router)
setup_exception_handlers(app)
app.add_middleware(LoggingMiddleware)