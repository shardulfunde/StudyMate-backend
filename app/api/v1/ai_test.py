from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.db.models.user import User
from app.schemas.mcq_test_generation import TestGenerationRequest,TestGenerationResponse
from app.tasks.generate_test import generate_random_resource_test,generate_relevant_test
from app.schemas.test_analysis import TestAnalysisRequest, TestAnalysisResponse
from app.tasks.get_test_analysis import get_test_analysis


router = APIRouter(
    prefix="/tests",
    tags=["MCQ Test Generation"]
)


@router.post("/generate", response_model=TestGenerationResponse)
def generate_test(
    request: TestGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    if request.scope_type in ["random_resource", "random_subject"]:
        return generate_random_resource_test(
            db=db,
            user=current_user,
            request=request,
        )

    elif request.scope_type in ["relevant_resource", "relevant_subject"]:
        return generate_relevant_test(
            db=db,
            user=current_user,
            request=request,
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid scope_type",
    )
    
@router.post("/analyze",response_model=TestAnalysisResponse)
def analyze_test(request:TestAnalysisRequest,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    return get_test_analysis(db,current_user,request)
