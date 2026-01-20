from claude_agent_sdk import ClaudeAgentOptions
from pydantic import BaseModel, Field
from typing import List

PROMPT = """
Eres un asistente de desarrollo que realizará cambios MENORES en código.
REGLAS ABSOLUTAS:
1. SOLO modificar archivos específicamente mencionados
2. NUNCA eliminar código sin reemplazo equivalente
3. Cambios máximos: 3-5 archivos por tarea
4. NO modificar: .gitignore, package-lock.json, archivos binarios

Se te brindará la siguiente información para lograr ello:
TAREA: Descripción de la tarea de Jira
ARCHIVOS A MODIFICAR: Posibles archivos a modificar

Proporciona SOLO el diff necesario (formato unified diff).
"""

schema = {
    "type": "object",
    "properties": {
        "changed_files": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "List of file paths that were changed"
        },
        "message": {
            "type": "string",
            "description": "Commit message summarizing the changes made"
        },
        "title": {
            "type": "string",
            "description": "Title for the pull request"
        },
        "body": {
            "type": "string",
            "description": "Body for the pull request"
        }
    },
    "required": ["changed_files", "message", "title", "body"]
}

class CommitInfo(BaseModel):
    """Modelo para información de commit y pull request"""
    changed_files: List[str] = Field(description="List of file paths that were changed")
    message: str = Field( description="Commit message summarizing the changes made")
    title: str = Field(description="Title for the pull request")
    body: str = Field(description="Body for the pull request")

programming_agent = ClaudeAgentOptions(
    system_prompt=PROMPT,
    allowed_tools=[
        "Read", "Edit", "Glob"],
    permission_mode='bypassPermissions',
    output_format={
        "type": "json_schema",
        "schema": CommitInfo.model_json_schema()
    },
    cwd="./tmp"
)