import os
from git import Repo
from typing import Optional, Dict, Any
from claude_agent_sdk import tool, create_sdk_mcp_server

CLONE_REPOSITORY_SCHEMA = {
    "type": "object",
    "properties": {
        "repository_url": {"type": "string"}
    },
    "required": ["repository_url"]
}

CREATE_BRANCH_SCHEMA = {
    "type": "object",
    "properties": {
        "jira_issue": {"type": "string"}
    },
    "required": ["jira_issue"]
}

COMMIT_FILES_SCHEMA = {
    "type": "object",
    "properties": {
        "changed_files": {
            "type": "object",
            "properties": {
                "type": "string"
            }
        },
        "message": {"type": "string"}
    },
    "required": ["changed_files", "message"]
}

AgnosticArgsType = Dict[str, Any]

class GitManager:
    def __init__(self, base_dir: Optional[str] = "./tmp"):
        self.base_dir = base_dir
        self.repository_instance = None
        pass
    
    @tool("clone_repository", "Clone remote repository", CLONE_REPOSITORY_SCHEMA)
    def clone_repository(self, args: AgnosticArgsType) -> str:
        repository_url = args.get("repository_url", None)
        repository_name = repository_url.split('/')[-1].replace('.git', '')
        repository_full_path = f"{self.base_dir}/{repository_name}"

        if os.path.exists(repository_full_path):
            self.repository_instance = Repo(repository_full_path)
            return repository_full_path
        
        self.repository_instance = Repo.clone_from(repository_url, repository_full_path)
        return repository_full_path

    def validate_repository_instance(self):
        if self.repository_instance is None:
            content_message = {
                "type": "text", 
                "text": "Error: Division by zero",
                "is_error": True
            }
            return True, [content_message]
        return False, []

    @tool("create_branch", "Create branch or valide if exists", CREATE_BRANCH_SCHEMA)
    def create_branch(self, args: AgnosticArgsType):
        jira_issue = args.get("jira_issue", None)
        message = None

        branch_name = f"feature/{jira_issue}"
        exists_remote_repository, error_information = self.validate_repository_instance()

        if exists_remote_repository:
            return error_information

        if branch_name not in [branch.name for branch in self.repository_instance.branches]:
            self.repository_instance.git.checkout('master')
            new_branch = self.repository_instance.create_head(branch_name)
            new_branch.checkout()
            message = f" Branch '{branch_name}': is created" 
            print(f"{message}")
        else:
            self.repository_instance.git.checkout(branch_name)
            message = f"Change to '{branch_name}' branch" 
            print(message)

        return {
            "content": [{
                "type": "text",
                "text": message
            }]
        }

    @tool("Create commit", "Create commit of changed files", COMMIT_FILES_SCHEMA)
    def create_commit(self, args: AgnosticArgsType):
        changed_files = args.get("changed_files")
        message = args.get("message")

        self.repository_instance.index.add([changed_files])
        
        self.repository_instance.index.commit(message)
        
        return {
            "content": [{
                "type": "text",
                "text": "Commit {message} was done"
            }]
        }

git_manager = GitManager()
git_manager = create_sdk_mcp_server(
    name="git_manager",
    version="1.0.0",
    tools=[git_manager.clone_repository, git_manager.create_branch, git_manager.create_commit]
)