from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.views import router as auth_router
from chat.views import router as chat_router


app = FastAPI(title="ITworkin", docs_url="/")


app.include_router(auth_router)
app.include_router(chat_router)

origins = [
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
