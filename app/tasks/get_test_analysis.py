from sqlalchemy.orm import Session
from langchain_cerebras import ChatCerebras
from fastapi import HTTPException,status
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.db.models.user import User
from app.schemas.test_analysis import TestAnalysisRequest,TestAnalysisResponse,TheoryTestAnalysisRequest,TheoryTestAnalysis
import json
from dotenv import load_dotenv
load_dotenv()


model = ChatCerebras(model="gpt-oss-120b")

def get_test_analysis(
    db: Session,
    user: User,
    request: TestAnalysisRequest
) -> TestAnalysisResponse:

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    parser = PydanticOutputParser(pydantic_object=TestAnalysisResponse)

    prompt = PromptTemplate(
        template="""
        You are an academic performance analyst.

        Analyze the student's performance by comparing:
        - The test questions
        - The correct answers
        - The student's selected answers

        Test Data:
        {test_data}

        Student Answers:
        {student_answers}

        Instructions:
        - Determine overall performance level.
        - Identify strong and weak concepts based on incorrect answers.
        - Detect recurring mistake patterns.
        - Highlight conceptual gaps.
        - Prioritize weak topics logically.
        - Provide a detailed, non-generic improvement roadmap.
        - Be specific and academically rigorous.
        - Do NOT hallucinate information not present in the test data.
        - Output ONLY valid JSON.
        - Follow the required schema exactly.

        {format_instructions}
        """,
        input_variables=["test_data", "student_answers"],
        partial_variables={
            "format_instructions": parser.get_format_instructions()
        },
    )

    chain = prompt | model | parser

    try:
        response = chain.invoke({
            "test_data": request.test.model_dump_json(),
            "student_answers": json.dumps(
                [ans.model_dump() for ans in request.student_answer]
            ),
        })
        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis generation failed: {str(e)}"
        )
def get_theory_test_analysis(
    db: Session,
    user: User,
    request: TheoryTestAnalysisRequest
) -> TheoryTestAnalysis:

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    parser = PydanticOutputParser(pydantic_object=TheoryTestAnalysis)

    prompt = PromptTemplate(
        template="""
        You are an academic evaluator.

        Evaluate the student's answers using:
        - The generated model answers
        - The maximum marks for each question
        - The original reference study material

        Test Data:
        {test_data}

        Student Answers:
        {student_answers}

        Reference Study Material:
        {reference_material}

        Instructions:
        - Compare student answer with model answer.
        - Use reference material for conceptual validation.
        - Award marks strictly within the maximum marks.
        - Be academically objective.
        - Identify missing concepts and weak explanations.
        - Provide question-wise feedback.
        - Provide overall performance feedback.
        - Do NOT hallucinate.
        - Output ONLY valid JSON.

        {format_instructions}
        """,
        input_variables=[
            "test_data",
            "student_answers",
            "reference_material"
        ],
        partial_variables={
            "format_instructions": parser.get_format_instructions()
        },
    )

    chain = prompt | model | parser

    try:
        response = chain.invoke({
            "test_data": request.theory_test.theory_test.model_dump_json(),
            "student_answers": json.dumps(
                [ans.model_dump() for ans in request.student_answer]
            ),
            "reference_material": json.dumps(
                request.theory_test.random_chunks
            )
        })

        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Theory analysis failed: {str(e)}"
        )


    
    

    