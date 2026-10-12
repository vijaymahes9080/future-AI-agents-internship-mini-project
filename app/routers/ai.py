from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import AIQuestionRequest, AIResponse
from app.services.ai_service import query_student_ai

router = APIRouter(prefix="/ai", tags=["Local AI Assistant"])

@router.post(
    "/ask",
    response_model=AIResponse,
    summary="Ask natural language questions about student records",
    description="Processes academic queries safely using controlled backend aggregations and optional local Ollama LLM integration."
)
async def ask_ai_endpoint(
    request: AIQuestionRequest,
    db: Session = Depends(get_db)
):
    result = await query_student_ai(db=db, question=request.question)
    return AIResponse(**result)
