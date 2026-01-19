import asyncio
import argparse
from claude_agent_sdk import (
    ClaudeSDKClient,
    AssistantMessage,
    ToolUseBlock,
    ToolResultBlock,
    TextBlock
)
from agents.programming import programming_agent

async def main(msg):

    repository_url = msg.get("repository_url", None)
    description = msg.get("description", None)
    jira_issue = msg.get("jira_issue", None)
    
    async with ClaudeSDKClient(options=programming_agent) as client:
        await client.query(
            f"""Resolve this issue 
            Jira Issue: {jira_issue} 
            Description: {description}
            from this repository url {repository_url}"""
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
                        print(f"💭 Claude says: {block.text[:100]}...")

            if hasattr(message, 'subtype') and message.subtype in ['success', 'error']:
                print(f"\n🎯 Task completed!")
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
    asyncio.run(main())