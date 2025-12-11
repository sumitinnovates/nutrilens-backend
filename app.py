from fastapi import FastAPI
from routes import auth_routes, food_scan_routes, notification_routes

app = FastAPI()

app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(food_scan_routes.router, prefix="/scans", tags=["Food Scans"])
app.include_router(notification_routes.router, prefix="/notifications", tags=["Notifications"])