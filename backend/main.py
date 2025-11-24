from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from routes import auth, chats, analytics, reports, meetings

app = FastAPI(
    title="ChatInsight Backend",
    description="API for ChatInsight — Conversational & Meeting Analyzer",
    version="1.0.0"
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
app.openapi_schema = None  

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Register routers ---
app.include_router(auth.router)
app.include_router(chats.router)
app.include_router(analytics.router)
app.include_router(reports.router)
app.include_router(meetings.router)


@app.get("/")
async def root():
    return {"message": "Welcome to ChatInsight API"}


