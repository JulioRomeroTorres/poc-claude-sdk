from datetime import datetime
from uuid import uuid4
from quart import Blueprint, Response, request

from app.presentation.api.dto import CreateTaskResquest, CreateTaskResponse

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/task", methods=["POST"])
async def create_task():

    data = await request.get_json()
    chat_request = CreateTaskResquest(**data)
    task_id = f"{uuid4()}"

    chat_response = CreateTaskResponse(
        message="",
        task_id=task_id,
    )

    return chat_response.model_dump(), 200

@api_bp.route("/tasks/status/<task_id>", methods=["GET"])
async def get_task_status(task_id: str):
    return {
        "session_id": str(session_id),
        "created_at": datetime.now().isoformat()
    }, 201


@api_bp.route("/health", methods=["GET"])
async def health():
    return {"status": "healthy"}, 200
