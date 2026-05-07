from app.core.deps import get_db,get_current_user
from app.db.models import User, Resource
from fastapi import HTTPException,status
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from app.db.models.user import User
from app.schemas.theory_test_generation import TheoryTestResponse,TheoryTestGenerationRequest,FinalTheoryResponse
from app.tasks.get_embeddings import get_random_chunks_from_subject,get_random_chunks_from_topic,get_relevant_chunks_for_test,get_relevant_chunks_for_subject
from sqlalchemy.orm import Session

model = ChatOpenAI(model="gpt-4o-mini")

from fastapi.responses import StreamingResponse
from langchain_core.output_parsers import StrOutputParser

def generate_random_theory_resource_test(
    db: Session,
    user: User,
    request: TheoryTestGenerationRequest,
):
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    
    if request.scope_type == "random_resource":
        random_chunk = get_random_chunks_from_topic(db, request.scope_id)
    elif request.scope_type == "random_subject":
        random_chunk = get_random_chunks_from_subject(db, request.scope_id)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="scope_type must be 'resource' or 'subject'")

    if not random_chunk:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No study material found")

    prompt = PromptTemplate(
        template="""
    You are StudyMate, a precise academic theory test generator.

    Generate exactly {number_of_questions} descriptive theory questions strictly based on the provided study material.

    MARKS DISTRIBUTION RULE:
    - Questions MUST include 2-mark, 3-mark, and 5-mark types.
    - Distribute marks as evenly as possible across 2, 3, and 5.
    - Every question must clearly specify its marks value.

    STRICT RULES:
    - Use ONLY the provided study material.
    - Do NOT use outside knowledge.
    - Do NOT hallucinate.
    - No markdown formatting (no ```json).
    - No explanations outside the JSON object.

    OUTPUT FORMAT: JSON-Lines (NDJSON)
    You must output EXACTLY {number_of_questions} lines.
    Every single line must be a valid JSON object with the following structure:
    {{"marks": 2, "question": "string", "answer": "string", "concept": "string"}}
    Do NOT wrap the output in a JSON array [ ].

    QUESTION QUALITY GUIDELINES:
    - NEVER ask trivial, direct definition questions (e.g., "What is soil?", "Define X").
    - Questions MUST be analytical, conceptual, or application-based.
    - Use prompts like "How", "Why", "Compare", "Analyze", "Justify", or present a scenario.
    - Difficulty level: {difficulty}
    - Language: {language}
    - Depth must match marks:
        - 2 marks → Provide a reason, compare two concepts briefly, or state the significance (NO basic definitions).
        - 3 marks → Explain a process, analyze a relationship, or describe a mechanism.
        - 5 marks → Detailed structured answer requiring multi-step reasoning, scenario analysis, or comprehensive evaluation.

    Study Material:
    {content}
    """,
        input_variables=["number_of_questions", "difficulty", "language", "content"],
    )
    chain = prompt | model | StrOutputParser()
    
    user.tests_generated_count += 1
    if request.scope_type == "random_resource":
        db.query(Resource).filter(Resource.id == request.scope_id).update(
            {"tests_generated_count": Resource.tests_generated_count + 1},
            synchronize_session=False
        )
    db.commit()

    def stream_generator():
        for chunk in chain.stream({
            "number_of_questions": request.number_of_questions,
            "difficulty": request.difficulty,
            "language": request.language,
            "content": random_chunk,
        }):
            yield chunk

    return StreamingResponse(stream_generator(), media_type="application/x-ndjson")

def generate_relevant_theory_test(
    db: Session,
    user: User,
    request: TheoryTestGenerationRequest,
):
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    
    if request.scope_type == "relevant_resource":
        content = get_relevant_chunks_for_test(db,request.scope_id,request.query)
    elif request.scope_type == "relevant_subject":
        content = get_relevant_chunks_for_subject(db,request.scope_id,request.query)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="scope_type must be 'relevant_resource' or 'relevant_subject'")

    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No relevant study material found")

    prompt = PromptTemplate(
        template="""
    You are StudyMate, a precise academic theory test generator.

    Generate exactly {number_of_questions} descriptive theory questions strictly based on the provided study material.

    FOCUS TOPICS:
    {query}

    The query may contain multiple topics.
    You must:
    - Cover ALL major topics mentioned in the query.
    - Distribute questions across those topics as evenly as possible.
    - Avoid generating all questions from a single topic.

    MARKS DISTRIBUTION RULE:
    - Questions MUST include 2-mark, 3-mark, and 5-mark types.
    - Distribute marks as evenly as possible across 2, 3, and 5.
    - Each question must clearly specify its marks value.

    STRICT RULES:
    - Use ONLY the provided study material.
    - Do NOT use outside knowledge.
    - Do NOT hallucinate.
    - Ignore portions of study material not related to the query topics.
    - If sufficient content is not available for a topic, reduce its coverage instead of fabricating information.
    - No markdown formatting (no ```json).
    - No explanations outside the JSON object.

    OUTPUT FORMAT: JSON-Lines (NDJSON)
    You must output EXACTLY {number_of_questions} lines.
    Every single line must be a valid JSON object with the following structure:
    {{"marks": 2, "question": "string", "answer": "string", "concept": "string"}}
    Do NOT wrap the output in a JSON array [ ].

    QUESTION QUALITY GUIDELINES:
    - NEVER ask trivial, direct definition questions (e.g., "What is soil?", "Define X").
    - Questions MUST be analytical, conceptual, or application-based.
    - Use prompts like "How", "Why", "Compare", "Analyze", "Justify", or present a scenario.
    - Difficulty level: {difficulty}
        - easy → conceptual understanding (no direct definitions)
        - medium → analyze relationships or mechanisms
        - hard → complex analytical reasoning and scenarios
    - Language: {language}
    - Depth must match marks:
        - 2 marks → Provide a reason, compare two concepts briefly, or state the significance (NO basic definitions).
        - 3 marks → Explain a process, analyze a relationship, or describe a mechanism.
        - 5 marks → Detailed structured answer requiring multi-step reasoning, scenario analysis, or comprehensive evaluation.
    - The "concept" field must clearly correspond to one of the query topics.

    Study Material:
    {content}
    """,
        input_variables=["number_of_questions", "difficulty", "language", "content", "query"],
    )

    chain = prompt | model | StrOutputParser()

    user.tests_generated_count += 1
    if request.scope_type == "relevant_resource":
        db.query(Resource).filter(Resource.id == request.scope_id).update(
            {"tests_generated_count": Resource.tests_generated_count + 1},
            synchronize_session=False
        )
        
    db.commit()

    def stream_generator():
        for chunk in chain.stream({
            "number_of_questions": request.number_of_questions,
            "difficulty": request.difficulty,
            "language": request.language,
            "content": content,
            "query": request.query,
        }):
            yield chunk

    return StreamingResponse(stream_generator(), media_type="application/x-ndjson")

