import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import computed_field
from pydantic_settings import BaseSettings
from typing import Optional

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from app.domain.message_store.cosmos_db_credentials import CosmosDbCredentials

class Settings(BaseSettings):
    app_name: str = "Orchestrator Agent System"
    api_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4")

    azure_openai_endpoint: str | None = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str | None = os.getenv("AZURE_OPENAI_API_KEY")
    azure_openai_deployment: str | None = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    azure_openai_api_version: str = os.getenv(
        "AZURE_OPENAI_API_VERSION", "2024-08-01-preview"
    )

    foundry_draft_agent_url: str | None = os.getenv("FOUNDRY_DRAFT_AGENT_URL")
    foundry_draft_agent_key: str | None = os.getenv("FOUNDRY_DRAFT_AGENT_KEY")
    use_remote_draft_agent: bool = os.getenv("USE_REMOTE_DRAFT_AGENT", "false").lower() == "true"
    remote_agent_timeout: float = float(os.getenv("REMOTE_AGENT_TIMEOUT", "30.0"))
    ssl_cert_file: str | None = os.getenv("SSL_CERT_FILE")
    requests_ca_bundle: str | None = os.getenv("REQUESTS_CA_BUNDLE")
    workflow_mode: str = os.getenv("WORKFLOW_MODE", "switch")

    enable_instrumentation: bool = os.getenv("ENABLE_INSTRUMENTATION", "false").lower() == "true"
    enable_sensitive_data: bool = os.getenv("ENABLE_SENSITIVE_DATA", "false").lower() == "true"
    otel_exporter_otlp_endpoint: str | None = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    applicationinsights_connection_string: str | None = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]

    cosmos_db_chat_storage_url: Optional[str] = None
    cosmos_db_chat_storage_db: Optional[str] = None
    cosmos_db_chat_storage_container: Optional[str] = None

    @computed_field
    def cosmos_chat_message_storage_credentials(self) -> CosmosDbCredentials:
        if not (self.cosmos_db_chat_storage_url and self.cosmos_db_chat_storage_db):
             pass 
             
        return CosmosDbCredentials(
            url=self.cosmos_db_chat_storage_url,
            database=self.cosmos_db_chat_storage_db,
            container=self.cosmos_db_chat_storage_container
        )

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
