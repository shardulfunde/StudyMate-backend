from pydantic import BaseModel,Field
from typing import List,Optional,Literal


#It will take this as request
class TestGenerationRequest(BaseModel):
    scope_type:Literal["random_resource","random_subject","relevant_resource","relevant_subject"]
    scope_id:str
    number_of_questions:Optional[int]=10
    language:Optional[str]="English"
    difficulty:Optional[str]="medium"
    query:Optional[str]=None
    
class test_metadata(BaseModel):
    topic:str=Field(...,description="The topic of the generated questions")
    language:str=Field(...,description="The language of the generated questions")
    difficulty:str=Field(...,description="The difficulty level of the generated questions")
    
class Question(BaseModel):
    question_text:str=Field(...,description="The text of the question")
    options:List[str]=Field(...,description="A list of 4 options for the question")
    correct_answer:int=Field(...,description="The index (0-3) of the correct answer in the options list")
    explanation:str=Field(...,description="The explanation for the correct answer")
    
class TestGenerationResponse(BaseModel):
    topic:str=Field(...,description="The topic of the generated questions")
    language:str=Field(...,description="The language of the generated questions")
    difficulty:str=Field(...,description="The difficulty level of the generated questions")
    questions:List[Question]=Field(...,description="A list of generated questions")
    
class FinalTestStreaming(BaseModel):
    test_metadata:test_metadata
    Questions:List[Question]
    