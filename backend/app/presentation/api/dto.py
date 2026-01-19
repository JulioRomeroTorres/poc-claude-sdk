from pydantic import BaseModel

class CreateTaskResquest(BaseModel):
    jira_issue: str
    description: str
    severity: int
    repository_url: str

class CreateTaskResponse(BaseModel):
    task_id: str
    message: str
