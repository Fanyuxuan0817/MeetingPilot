from fastapi import APIRouter

from app.api.v1 import meetings, transcripts, summaries, actions, decisions, qa, chat

api_router = APIRouter()

api_router.include_router(meetings.router, prefix="/meetings", tags=["meetings"])
api_router.include_router(transcripts.router, tags=["transcripts"])
api_router.include_router(summaries.router, tags=["summaries"])
api_router.include_router(actions.router, tags=["actions"])
api_router.include_router(decisions.router, tags=["decisions"])
api_router.include_router(qa.router, tags=["qa"])
api_router.include_router(chat.router, tags=["chat"])
