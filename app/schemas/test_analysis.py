from pydantic import BaseModel,Field
from typing import List
from app.schemas.mcq_test_generation import TestGenerationResponse

class StudentAnswer(BaseModel):
    question_index: int
    selected_option: int



class TestAnalysisResponse(BaseModel):
    topic:str = Field(...,description="Topic of the test analysis")
    language:str = Field(...,description="Language of the test analysis")
    difficulty:str = Field(...,description="Difficulty of the test")
    detailed_desciption:str = Field(...,description="A comprehensive explanation of the student's overall performance in the test, including strengths, weaknesses, common mistake patterns, conceptual gaps, time management insights, and behavioral observations derived from answer analysis.")
    topics_to_focus:List[str] = Field(...,description="A structured list of specific concepts, chapters, or subtopics where the student demonstrated weak understanding, frequent errors, low accuracy, or slow response time, prioritized by importance and impact on overall performance.")
    detailed_plan_to_improve:List[str] = Field(...,description="A step-by-step, actionable improvement roadmap tailored to the student's performance. It should include revision strategies, practice recommendations, concept reinforcement methods, mock test scheduling, error correction techniques, and measurable progress checkpoints.")
    
    
class TestAnalysisRequest(BaseModel):
    test:TestGenerationResponse = Field(...,description="Detailed test schema")
    student_answer:StudentAnswer = Field(...,description="Question number and answer choosen by student")