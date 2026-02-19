from sqlalchemy.orm import Session
from langchain_cerebras import ChatCerebras
from fastapi import HTTPException,status
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.db.models.user import User
from app.schemas.test_analysis import TestAnalysisRequest,TestAnalysisResponse
from dotenv import load_dotenv
load_dotenv()


model = ChatCerebras(model="gpt-oss-120b")

def get_test_analysis(
    db: Session,
    user: User,
    request: TestAnalysisRequest
) -> TestAnalysisResponse:


    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")

    parser = PydanticOutputParser(pydantic_object=TestAnalysisResponse)

    prompt = PromptTemplate(
        template="""
        You are an academic performance analyst.

        Analyze the following test and generate a structured performance report.

        Test Data:
        {test_data}

        Return output strictly in this format:
        {format_instructions}

        Important:
        - Be specific.
        - Avoid generic advice.
        - Focus on conceptual depth.
        - Prioritize weaknesses logically.
        """,
        input_variables=["test_data"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    test_json = request.test.model_dump_json()

    chain = prompt | model | parser

    try:
        response = chain.invoke({"test_data": test_json})
        return response

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Analysis generation failed: {str(e)}")

    
    
    
    