from app.core.deps import get_db,get_current_user
from app.db.models.resource import Resource
from fastapi import HTTPException,status
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from app.db.models.user import User
from app.schemas.mcq_test_generation import TestGenerationRequest,TestGenerationResponse
from app.tasks.get_embeddings import get_random_chunks_from_subject,get_random_chunks_from_topic,get_relevant_chunks_for_test,get_relevant_chunks_for_subject
from sqlalchemy.orm import Session

model = ChatOpenAI(model="gpt-5-nano")



#Lets stream this response(Nah streaming is too defficult I gave up)
def generate_random_resource_test(
    db: Session,
    user: User,
    request: TestGenerationRequest,
):
    
    if request.scope_type == "random_resource":
        random_chunk = get_random_chunks_from_topic(db, request.scope_id)

    elif request.scope_type == "random_subject":
        random_chunk = get_random_chunks_from_subject(db, request.scope_id)
    
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="scope_type must be 'resource' or 'subject'")

    if not random_chunk:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No study material found")

    parser = PydanticOutputParser(pydantic_object=TestGenerationResponse)

    prompt = PromptTemplate(
        template="""
        You are StudyMate, an intelligent academic test generator.

        Generate {number_of_questions} high-quality MCQs strictly based on the study material.

        Rules:
        - Use ONLY given content.
        - No hallucination.
        - No markdown.
        - No extra text.
        - Exactly 4 options.
        - One correct answer.
        - Difficulty: {difficulty}
        - Language: {language}

        Difficulty Guide:
        - easy → recall
        - medium → understanding
        - hard → analytical reasoning

        Study Material:
        {content}

        {format_instructions}
        """,
        input_variables=[
            "number_of_questions",
            "difficulty",
            "language",
            "content",
        ],
        partial_variables={
            "format_instructions": parser.get_format_instructions()
        },
    )

    chain = prompt | model | parser
    
    result = chain.invoke({
        "number_of_questions": request.number_of_questions,
        "difficulty": request.difficulty,
        "language": request.language,
        "content": random_chunk,
    })
    user.tests_generated_count+=1
    
    if request.scope_type == "random_resource":
        db.query(Resource).filter(Resource.id == request.scope_id).update(
            {"tests_generated_count": Resource.tests_generated_count + 1},
            synchronize_session=False
        )
    return result


#Generated different function for this because the model must know the query
def generate_relevant_test(
    db: Session,
    user: User,
    request: TestGenerationRequest,
):

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    if not request.query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Query is required for relevant test")

    if request.scope_type == "relevant_resource":
        content = get_relevant_chunks_for_test(db,request.scope_id,request.query)

    elif request.scope_type == "relevant_subject":
        content = get_relevant_chunks_for_subject(db,request.scope_id,request.query)

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="scope_type must be 'relevant_resource' or 'relevant_subject'")

    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No relevant study material found")

    parser = PydanticOutputParser(pydantic_object=TestGenerationResponse)

    prompt = PromptTemplate(
        template="""
            You are StudyMate.

            Generate {number_of_questions} MCQs strictly focused on this topic:
            "{query}"

            All questions must directly relate to the query.

            Rules:
            - Use ONLY given content.
            - No hallucination.
            - Exactly 4 options.
            - One correct answer.
            - Difficulty: {difficulty}
            - Language: {language}
            - No markdown.
            - No extra text.

            Study Material:
            {content}

            {format_instructions}
            """,
        input_variables=[
            "number_of_questions",
            "difficulty",
            "language",
            "content",
            "query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | model | parser

    user.tests_generated_count += 1

    if request.scope_type == "relevant_resource":
        db.query(Resource).filter(Resource.id == request.scope_id).update(
            {"tests_generated_count": Resource.tests_generated_count + 1},
            synchronize_session=False
        )
        
    db.commit()
    return chain.invoke({
        "number_of_questions": request.number_of_questions,
        "difficulty": request.difficulty,
        "language": request.language,
        "content": content,
        "query": request.query,
    })

