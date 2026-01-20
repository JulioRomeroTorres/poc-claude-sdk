import asyncio
import argparse
from claude_agent_sdk import (
    ClaudeSDKClient,
    AssistantMessage,
    ToolUseBlock,
    ToolResultBlock,
    TextBlock,
    ResultMessage
)
from agents.programming import programming_agent, CommitInfo
from tools.git_manager import GitManager
import os
import shutil

def clean_folder(folder_path: str):
    
    if not os.path.exists(folder_path):
        print(f"⚠️  La carpeta '{folder_path}' no existe")
        return
    
    try:
        # Listar contenido antes de borrar (opcional para debug)
        contenido = os.listdir(folder_path)
        print(f"🗑️  Borrando {len(contenido)} elementos de: {folder_path}")
        
        # Eliminar todo el contenido
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path)
                print(f"  ✗ Archivo: {item}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"  ✗ Carpeta: {item}")
        
        print(f"✅ Carpeta '{folder_path}' limpiada completamente")
        
    except Exception as e:
        print(f"❌ Error al limpiar la carpeta: {e}")

async def main(msg):

    repository_url = msg.get("repository_url", None)
    description = msg.get("description", None)
    jira_issue = msg.get("jira_issue", None)

    git_manager = GitManager()
    git_manager.clone_repository(repository_url)
    git_manager.create_branch(jira_issue)
    task_result = None

    async with ClaudeSDKClient(options=programming_agent) as client:
        await client.query(
            f"""Resolve this issue 
            Jira Issue: {jira_issue} 
            Description: {description}
            from this folder {git_manager.repository_full_path}"""
        )

        async for message in client.receive_messages():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, ToolUseBlock):
                        if block.name == "Write":
                            file_path = block.input.get("file_path", "")
                            print(f"🔨 Creating: {file_path}")
                    elif isinstance(block, ToolResultBlock):
                        print(f"✅ Completed tool {block.tool_use_id} execution")
                    elif isinstance(block, TextBlock):
                        print(f"💭 Claude says: {block.text}...")
            
            if isinstance(message, ResultMessage) and message.structured_output:
                task_result = CommitInfo.model_validate(message.structured_output)
                print(f"\n🧾 Structured Output: {task_result}\n")

            if hasattr(message, 'subtype') and message.subtype in ['success', 'error']:
                if message.subtype == 'success':
                    git_manager.create_commit(task_result.changed_files, task_result.message)
                    git_manager.push_and_create_pr(task_result.title, task_result.body)
                    print(f"\n🎯 Task completed!")

                current_dir = os.path.dirname(os.path.abspath(__file__))
                tmp_dir = os.path.join(current_dir, 'tmp')
                clean_folder(tmp_dir)
                break

def configurar_argumentos():

    parser = argparse.ArgumentParser(
        description='Agente Claude para automatización Git'
    )
    
    parser.add_argument(
        '--description', 
        required=True,
        help='Description of jira issue'
    )
    
    parser.add_argument(
        '--repo', 
        help='URL del repositorio Git'
    )
    
    parser.add_argument(
        '--jira_issue',
        help='Issue de Jira'
    )
    
    return parser.parse_args()


if __name__ == "__main__":
    parser_args = configurar_argumentos()
    msg = {
        "repository_url": parser_args.repo,
        "jira_issue": parser_args.jira_issue,
        "description": parser_args.description
    }
    asyncio.run(main(msg))