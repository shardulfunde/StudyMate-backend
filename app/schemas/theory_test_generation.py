from pydantic import BaseModel,Field
from typing import List,Optional,Literal

class question(BaseModel):
    marks:int = Field(...,description="Number of marks the question is for")
    question:str = Field(...,description="The actual question")
    answer:str = Field(...,description="The answer of the question according to pattern")
    concept:str = Field(...,description="From which concept the question is from")
    
    
class TheoryTestResponse(BaseModel):
    difficulty:str = Field(...,description="The difficulty of the test")
    language:str = Field(...,description="The language in which test is generated")
    questions:List[question] = Field(...,description="The list of questions")
    
    
class FinalTheoryResponse(BaseModel):
    theory_test:TheoryTestResponse
    random_chunks:List[str] = Field(...,description="The reference from which the test is generated")
    
class TheoryTestGenerationRequest(BaseModel):
    scope_type:Literal["random_resource","random_subject","relevant_resource","relevant_subject"]
    scope_id:str
    number_of_questions:Optional[int]=10
    language:Optional[str]="English"
    difficulty:Optional[str]="medium"
    query:Optional[str]=None