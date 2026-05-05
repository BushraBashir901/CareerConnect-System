from fastapi import APIRouter

#import endpoints
from app.api.v1.endpoints import (
    interview_api, job_api, report_api, company_api,
    job_application_api,user_api,auth_api,team_api,team_invitation_api,conversation_api,chat_ws_api)

router = APIRouter()

router.include_router(job_api.router)
router.include_router(user_api.router) 
router.include_router(report_api.router)
router.include_router(company_api.router)
router.include_router(job_application_api.router)
router.include_router(interview_api.router)
router.include_router(auth_api.router)
router.include_router(team_api.router)
router.include_router(team_invitation_api.router)
router.include_router(conversation_api.router)
router.include_router(chat_ws_api.router)


