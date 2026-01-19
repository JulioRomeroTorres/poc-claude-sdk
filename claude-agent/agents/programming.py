from claude_agent_sdk import ClaudeAgentOptions
from tools.git_manager import git_manager

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

programming_agent = ClaudeAgentOptions(
    system_prompt=PROMPT,
    mcp_servers={
        "git_manager": git_manager
        },
    allowed_tools=[
        "Read", "Edit", "Glob",
        "mcp__git_manager_clone", "mcp__git_manager__branch", "mcp__git_manager__commit"],
    permission_mode='acceptEdits',
    cwd="./tmp"
)