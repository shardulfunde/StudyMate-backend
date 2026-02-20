from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.db.models.user import User
from app.schemas.mcq_test_generation import TestGenerationRequest,TestGenerationResponse
from app.schemas.theory_test_generation import FinalTheoryResponse,TheoryTestGenerationRequest
from app.tasks.generate_test import generate_random_resource_test,generate_relevant_test
from app.tasks.generate_theory_test import generate_random_theory_resource_test,generate_relevant_theory_test
from app.schemas.test_analysis import TestAnalysisRequest, TestAnalysisResponse,TheoryTestAnalysisRequest,TheoryTestAnalysis
from app.tasks.get_test_analysis import get_test_analysis,get_theory_test_analysis


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


@router.post("/theorytest/generate",response_model=FinalTheoryResponse)
def generate_theory_test(request:TheoryTestGenerationRequest,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    if request.scope_type in ["random_resource", "random_subject"]:
        return generate_random_theory_resource_test(
            db=db,
            user=current_user,
            request=request,
        )

    elif request.scope_type in ["relevant_resource", "relevant_subject"]:
        return generate_relevant_theory_test(
            db=db,
            user=current_user,
            request=request,
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid scope_type",
    )
    
@router.post("/theorytest/analyze",response_model=TheoryTestAnalysis)
def generate_theory_test_analysis(request:TheoryTestAnalysisRequest,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    return get_theory_test_analysis(db,current_user,request)