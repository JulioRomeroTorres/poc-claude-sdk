import os
from git import Repo, GitCommandError
from typing import Optional, Dict, Any, List
import requests
from dotenv import load_dotenv

load_dotenv()

class GitManager:
    def __init__(self, base_dir: Optional[str] = "./tmp"):
        self.base_dir = base_dir
        self.repository_instance = None
        self.repository_full_path = None
        pass
    
    def clone_repository(self, repository_url: str) -> str:
        self.repository_url = repository_url
        repository_name = repository_url.split('/')[-1].replace('.git', '')
        repository_full_path = f"{self.base_dir}/{repository_name}"
        self.repository_full_path = repository_full_path

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

    def create_branch(self, jira_issue: str, reference_branch: Optional[str] = "master"):
        message = None

        branch_name = f"feature/{jira_issue}"
        exists_remote_repository, error_information = self.validate_repository_instance()

        if exists_remote_repository:
            return error_information

        if branch_name not in [branch.name for branch in self.repository_instance.branches]:
            self.repository_instance.git.checkout(reference_branch)
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

    def create_commit(self, changed_files: List[str], message: str):
        exists_remote_repository, error_information = self.validate_repository_instance()
        if exists_remote_repository:
            return error_information

        self.repository_instance.index.add(changed_files)
        
        self.repository_instance.index.commit(message)
        
        return {
            "content": [{
                "type": "text",
                "text": "Commit {message} was done"
            }]
        }

    def format_url_for_authentication(self) -> str:
        github_domain = "github.com"
        repository_path = self.repository_url.split(github_domain)

        print(f"split repository_path: {repository_path}")
        token = os.getenv("GITHUB_TOKEN")
        username = os.getenv("GITHUB_USERNAME")

        auth_url = f"https://{username}:{token}@{github_domain}{repository_path[-1]}"
        print(f"auth_url {auth_url}")
        return auth_url

    def push_and_create_pr(self, title: str, body: str, target_branch:Optional[str] = "master"):

        exists_remote_repository, error_information = self.validate_repository_instance()
        if exists_remote_repository:
            return error_information
        
        auth_url = self.format_url_for_authentication()
        self.repository_instance.remote().set_url(auth_url)

        try:
            current_branch = self.repository_instance.active_branch.name
            print(f"📤 Pushing branch '{current_branch}' to origin...")
            
            push_info = self.repository_instance.remote().push(
                refspec=f"{current_branch}:{current_branch}",
                set_upstream=True
            )
            
            print(f"✅ Push successful: {push_info}")
            
            pr_url = self.create_github_pr(
                title=title,
                body=body,
                head_branch=current_branch,
                base_branch=target_branch
            )
        
            return {
                "content": [{
                    "type": "text",
                    "text": f"✅ Push completed and PR created: {pr_url}"
                }]
            }

        except GitCommandError as e:
            print(f"❌ Push failed: {str(e)}")
            return {"error": f"Push failed: {str(e)}"}

    def create_github_pr(self, title: str, body: str, head_branch: str, base_branch: str = "main") -> str:
        print("Creating GitHub Pull Request...")
        if "github.com" in self.repository_url:
            parts = self.repository_url.rstrip('.git').split('/')
            owner = parts[-2]
            repo_name = parts[-1]
            
            token = os.getenv("GITHUB_TOKEN")
            if not token:
                return "Error: GITHUB_TOKEN no configurado"
            
            url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls"
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            data = {
                "title": title,
                "body": body,
                "head": head_branch,
                "base": base_branch
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                response_github_api = response.json()
                print(f"✅ Pull Request created successfully! {response_github_api}")
                return response_github_api["html_url"]
            raise Exception(f"❌ Failed to create PR: {response.status_code} - {response.text}")
                
        return "Error: Solo soporta repositorios GitHub por ahora"