from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Dict, Optional
from ..services.database import get_session
from ..models.message import Message
from ..models.conversation import Conversation
from ..services.conversation_service import ConversationService
from ..services.task_service import TaskService
from pydantic import BaseModel
import uuid
import re
from ..mcp_server.server import mcp_server


router = APIRouter()


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    metadata: Optional[Dict] = {}


class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    tool_calls: Optional[list] = []
    timestamp: str


@router.post("/chat")
def chat_endpoint(
    user_id: str,  # This comes from the path parameter and authentication
    chat_request: ChatRequest,
    session: Session = Depends(get_session)
) -> ChatResponse:
    """
    Main chat endpoint that handles user messages and returns AI responses.
    This connects to the MCP server to handle task operations.
    """
    # Handle both UUID and non-UUID user IDs
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        # If it's not a valid UUID, generate a consistent UUID from the string
        user_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, user_id)

    # Initialize services
    conversation_service = ConversationService(session)
    task_service = TaskService(session)

    # Get or create conversation
    conversation = None
    if chat_request.conversation_id:
        try:
            conv_id = uuid.UUID(chat_request.conversation_id)
            conversation = conversation_service.get_conversation_by_id(conv_id, user_uuid)
        except ValueError:
            # Invalid UUID format
            pass

    if not conversation:
        conversation = conversation_service.create_conversation(
            user_id=user_uuid,
            title=f"Chat started {chat_request.message[:30]}..."
        )

    # Create message in database
    user_message = Message(
        conversation_id=conversation.conversation_id,
        sender_type="user",
        content=chat_request.message
    )
    session.add(user_message)
    session.commit()

    # Process the message using the AI agent and MCP tools
    try:
        ai_response = process_user_message_with_ai(
            user_id=user_id,
            user_message=chat_request.message,
            task_service=task_service
        )
    except Exception as e:
        print(f"Error processing user message: {str(e)}")
        # Return a generic error response
        ai_response = {
            'response': "I'm sorry, I encountered an error processing your request. Please try again.",
            'tool_calls': []
        }

    # Create assistant message in database
    assistant_message = Message(
        conversation_id=conversation.conversation_id,
        sender_type="assistant",
        content=ai_response['response']
    )
    session.add(assistant_message)
    session.commit()

    return ChatResponse(
        conversation_id=str(conversation.conversation_id),
        response=ai_response['response'],
        tool_calls=ai_response.get('tool_calls', []),
        timestamp=str(assistant_message.timestamp)
    )


@router.get("/tasks")
def get_user_tasks(
    user_id: str,
    status: str = "all",
    session: Session = Depends(get_session)
):
    """Get all tasks for a user"""
    # Handle both UUID and non-UUID user IDs
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        # If it's not a valid UUID, generate a consistent UUID from the string
        user_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, user_id)
    task_service = TaskService(session)

    tasks = task_service.get_user_tasks(
        user_id=user_uuid,
        status_filter=status
    )

    return {
        "tasks": [
            {
                "task_id": str(t.task_id),
                "title": t.title,
                "description": t.description,
                "status": t.status,
                "priority": t.priority,
                "created_at": t.created_at.isoformat(),
                "updated_at": t.updated_at.isoformat(),
                "completed_at": t.completed_at.isoformat() if t.completed_at else None
            }
            for t in tasks
        ],
        "total": len(tasks),
        "status_filter": status
    }


@router.post("/tasks")
def create_task(
    user_id: str,
    task_data: dict,
    session: Session = Depends(get_session)
):
    """Create a new task for a user"""
    # Handle both UUID and non-UUID user IDs
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        # If it's not a valid UUID, generate a consistent UUID from the string
        user_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, user_id)
    task_service = TaskService(session)

    task = task_service.create_task(user_uuid, task_data)

    return {
        "task_id": str(task.task_id),
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
        "completed_at": task.completed_at.isoformat() if task.completed_at else None
    }


@router.put("/tasks/{task_id}")
def update_task(
    user_id: str,
    task_id: str,
    task_data: dict,
    session: Session = Depends(get_session)
):
    """Update a specific task for a user"""
    # Handle both UUID and non-UUID user IDs
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        # If it's not a valid UUID, generate a consistent UUID from the string
        user_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, user_id)

    # Handle both UUID and non-UUID task IDs
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        # If it's not a valid UUID, generate a consistent UUID from the string
        task_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, task_id)
    task_service = TaskService(session)

    task = task_service.update_task(user_uuid, task_uuid, task_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "task_id": str(task.task_id),
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
        "completed_at": task.completed_at.isoformat() if task.completed_at else None
    }


@router.delete("/tasks/{task_id}")
def delete_task(
    user_id: str,
    task_id: str,
    session: Session = Depends(get_session)
):
    """Delete a specific task for a user"""
    # Handle both UUID and non-UUID user IDs
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        # If it's not a valid UUID, generate a consistent UUID from the string
        user_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, user_id)

    # Handle both UUID and non-UUID task IDs
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        # If it's not a valid UUID, generate a consistent UUID from the string
        task_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, task_id)
    task_service = TaskService(session)

    success = task_service.delete_task(user_uuid, task_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"message": "Task deleted successfully"}


def process_user_message_with_ai(user_id: str, user_message: str, task_service: TaskService) -> Dict:
    """
    Process user message using natural language and execute appropriate task operations.
    This simulates the AI agent behavior until we integrate with OpenAI.
    """
    message_lower = user_message.lower().strip()

    # Define patterns for different commands
    patterns = {
        'add_task': r'(add|create|make|new)\s+(a\s+)?(task|todo|to-do|item)\s+(to|for|about|that|which)\s+(.+?)|(?:add|create|make|new)\s+(.+?)\s+(?:as\s+a\s+)?(task|todo|to-do)',
        'list_tasks': r'(show|list|display|see|view)\s+(my\s+)?(tasks|todos|to-dos|items|list)',
        'complete_task': r'(complete|finish|done|mark)\s+(task|todo|item)\s*(\d+|\w+)|mark\s+(task|todo)\s*(\d+|\w+)\s+as\s+complete|complete\s+(task|todo)\s*(\d+|\w+)|(complete|finish|done|mark)\s+(the\s+)?(.+?)\s+(task)',
        'update_task': r'(update|change|modify|edit)\s+(task|todo)\s*(\d+|\w+)|change\s+(task|todo)\s*(\d+|\w+)|(update|change|modify|edit)\s+(the\s+)?(.+?)\s+(task|to)',
        'delete_task': r'(delete|remove|eliminate)\s+(task|todo|item)\s*(\d+|\w+)|(delete|remove|eliminate)\s+(the\s+)?(.+?)\s+(task)'
    }

    # Execute appropriate tool based on the detected command using regex patterns
    # Check for add_task pattern first
    add_match = re.search(patterns['add_task'], user_message, re.IGNORECASE)
    if add_match:
        # Extract task title from the message
        title_groups = add_match.groups()
        # The pattern has two alternatives separated by |
        # First alternative: (add|create|make|new)\s+(a\s+)?(task|todo|to-do|item)\s+(to|for|about|that|which)\s+(.+?)
        # Second alternative: (?:add|create|make|new)\s+(.+?)\s+(?:as\s+a\s+)?(task|todo|to-do)
        # So groups are: (0=full match, 1=verb, 2=a, 3=task_type, 4=preposition, 5=title_first_alt, 6=title_second_alt, 7=task_type_alt)
        title = title_groups[5] if title_groups[5] else title_groups[6]  # Get the matched title from either alternative
        if title:
            title = title.strip().split('.')[0]  # Take only the first sentence if multiple
            result = mcp_server.execute_tool('add_task', user_id=user_id, title=title)
            if result['success']:
                return {
                    'response': result['message'],
                    'tool_calls': [{'name': 'add_task', 'arguments': {'title': title}, 'result': result}]
                }
            else:
                return {
                    'response': f"Sorry, I couldn't add that task: {result['message']}",
                    'tool_calls': []
                }
        else:
            # If we can't extract the title, ask for clarification
            return {
                'response': "I'd be happy to help you add a task. Could you please tell me what task you'd like to add?",
                'tool_calls': []
            }

    # Check for list_tasks pattern
    elif re.search(patterns['list_tasks'], user_message, re.IGNORECASE):
        # Determine if user wants pending or completed tasks
        status = "all"
        if 'pending' in message_lower or 'incomplete' in message_lower:
            status = "pending"
        elif 'completed' in message_lower or 'done' in message_lower:
            status = "completed"

        result = mcp_server.execute_tool('list_tasks', user_id=user_id, status=status)
        if result['success']:
            if result['count'] == 0:
                status_text = f"{status} " if status != "all" else ""
                response = f"You don't have any {status_text}tasks right now."
            else:
                status_text = f"{status} " if status != "all" else ""
                response = f"Here are your {status_text}tasks:\n"
                for i, task in enumerate(result['tasks'][:5], 1):  # Limit to first 5 tasks
                    completed_str = "✓" if task['completed'] else "○"
                    priority_str = f" ({task['priority']} priority)" if task['priority'] != 'medium' else ""
                    response += f"\n{i}. {completed_str} {task['title']}{priority_str}"

                if len(result['tasks']) > 5:
                    response += f"\n\n... and {len(result['tasks']) - 5} more tasks."

            return {
                'response': response,
                'tool_calls': [{'name': 'list_tasks', 'arguments': {'status': status}, 'result': result}]
            }
        else:
            return {
                'response': f"Sorry, I couldn't retrieve your tasks: {result['message']}",
                'tool_calls': []
            }

    # Check for complete_task pattern
    elif re.search(patterns['complete_task'], user_message, re.IGNORECASE):
        # Try to identify which task to complete
        # This is a simplified implementation - in a real app, we'd have better NLP
        result = mcp_server.execute_tool('list_tasks', user_id=user_id, status='pending')
        if result['success'] and result['count'] > 0:
            # Find the first pending task that matches keywords in the user's message
            task_to_complete = None
            for task in result['tasks']:
                if any(keyword in user_message.lower() for keyword in task['title'].lower().split()):
                    task_to_complete = task
                    break

            # If no keyword match, just pick the first task
            if not task_to_complete and len(result['tasks']) > 0:
                task_to_complete = result['tasks'][0]

            if task_to_complete:
                complete_result = mcp_server.execute_tool('complete_task', user_id=user_id, task_id=task_to_complete['id'])
                if complete_result['success']:
                    return {
                        'response': complete_result['message'],
                        'tool_calls': [{'name': 'complete_task', 'arguments': {'task_id': task_to_complete['id']}, 'result': complete_result}]
                    }
                else:
                    return {
                        'response': f"Sorry, I couldn't complete that task: {complete_result['message']}",
                        'tool_calls': []
                    }
            else:
                return {
                    'response': "I couldn't identify which task you want to complete. Could you please specify the task?",
                    'tool_calls': []
                }
        else:
            return {
                'response': "You don't have any pending tasks to complete.",
                'tool_calls': []
            }

    # Check for update_task pattern
    elif re.search(patterns['update_task'], user_message, re.IGNORECASE):
        # Try to identify which task to update and what to change
        result = mcp_server.execute_tool('list_tasks', user_id=user_id, status='all')
        if result['success'] and result['count'] > 0:
            # First, try to extract the task name from the pattern match
            update_match = re.search(patterns['update_task'], user_message, re.IGNORECASE)
            if update_match:
                # Groups: (0=full, 1-2 for first alt, 3-5 for second alt)
                # Second alternative: (update|change|modify|edit)\s+(the\s+)?(.+?)\s+(task|to)
                task_name_from_pattern = update_match.group(4) if update_match.group(4) else update_match.group(5)  # Get the task name from pattern

                # Find a task that matches the extracted name or keywords in the user's message
                task_to_update = None
                if task_name_from_pattern:
                    for task in result['tasks']:
                        if task_name_from_pattern.lower() in task['title'].lower():
                            task_to_update = task
                            break

                # If not found by pattern, try to match by keywords in the message
                if not task_to_update:
                    for task in result['tasks']:
                        if any(keyword in user_message.lower() for keyword in task['title'].lower().split()):
                            task_to_update = task
                            break

                if task_to_update:
                    # Extract what the user wants to update (title, description, priority, etc.)
                    # For simplicity, we'll update the title with the new description from the message
                    update_match_new = re.search(r'(update|change|modify|edit)\s+' + re.escape(task_to_update['title']) + r'\s+to\s+(.+)', user_message, re.IGNORECASE)
                    if not update_match_new:
                        update_match_new = re.search(r'(update|change|modify|edit)\s+(.+)', user_message, re.IGNORECASE)

                    new_title = task_to_update['title']
                    if update_match_new and update_match_new.group(2):
                        extracted_content = update_match_new.group(2).strip()
                        # If the user said something like "update task to add more details", use that as new title
                        if 'to' in extracted_content.lower():
                            to_parts = extracted_content.split('to', 1)
                            if len(to_parts) > 1:
                                new_title = to_parts[1].strip()

                    update_result = mcp_server.execute_tool('update_task', user_id=user_id, task_id=task_to_update['id'], title=new_title)
                    if update_result['success']:
                        return {
                            'response': update_result['message'],
                            'tool_calls': [{'name': 'update_task', 'arguments': {'task_id': task_to_update['id'], 'title': new_title}, 'result': update_result}]
                        }
                    else:
                        return {
                            'response': f"Sorry, I couldn't update that task: {update_result['message']}",
                            'tool_calls': []
                        }
                else:
                    return {
                        'response': "I couldn't identify which task you want to update. Could you please specify the task?",
                        'tool_calls': []
                    }
            else:
                return {
                    'response': "I couldn't identify which task you want to update. Could you please specify the task?",
                    'tool_calls': []
                }
        else:
            return {
                'response': "You don't have any tasks to update.",
                'tool_calls': []
            }

    # Check for delete_task pattern
    elif re.search(patterns['delete_task'], user_message, re.IGNORECASE):
        # Try to identify which task to delete
        result = mcp_server.execute_tool('list_tasks', user_id=user_id, status='all')
        if result['success'] and result['count'] > 0:
            # Find a task that matches keywords in the user's message
            task_to_delete = None
            for task in result['tasks']:
                if any(keyword in user_message.lower() for keyword in task['title'].lower().split()):
                    task_to_delete = task
                    break

            # If no keyword match, just pick the first task as a fallback
            if not task_to_delete and len(result['tasks']) > 0:
                task_to_delete = result['tasks'][0]

            if task_to_delete:
                delete_result = mcp_server.execute_tool('delete_task', user_id=user_id, task_id=task_to_delete['id'])
                if delete_result['success']:
                    return {
                        'response': delete_result['message'],
                        'tool_calls': [{'name': 'delete_task', 'arguments': {'task_id': task_to_delete['id']}, 'result': delete_result}]
                    }
                else:
                    return {
                        'response': f"Sorry, I couldn't delete that task: {delete_result['message']}",
                        'tool_calls': []
                    }
            else:
                return {
                    'response': "I couldn't identify which task you want to delete. Could you please specify the task?",
                    'tool_calls': []
                }
        else:
            return {
                'response': "You don't have any tasks to delete.",
                'tool_calls': []
            }

    else:
        # Default response for unrecognized commands
        return {
            'response': f"I received your message: '{user_message}'. I'm an AI assistant for managing your tasks. You can ask me to add, view, update, complete, or delete tasks.",
            'tool_calls': []
        }




@router.get("/conversations")
def get_user_conversations(
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    sort_by: str = "updated_at",
    order: str = "desc",
    session: Session = Depends(get_session)
):
    """Get all conversations for a user"""
    # Handle both UUID and non-UUID user IDs
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        # If it's not a valid UUID, generate a consistent UUID from the string
        user_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, user_id)
    conversation_service = ConversationService(session)

    conversations = conversation_service.get_user_conversations(
        user_id=user_uuid,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        order=order
    )

    return {
        "conversations": [
            {
                "conversation_id": str(c.conversation_id),
                "title": c.title,
                "created_at": c.created_at.isoformat(),
                "updated_at": c.updated_at.isoformat(),
                "status": c.status
            }
            for c in conversations
        ],
        "total": len(conversations),
        "limit": limit,
        "offset": offset
    }


@router.get("/conversations/{conversation_id}")
def get_conversation_details(
    user_id: str,
    conversation_id: str,
    session: Session = Depends(get_session)
):
    """Get details for a specific conversation"""
    # Handle both UUID and non-UUID user IDs
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        # If it's not a valid UUID, generate a consistent UUID from the string
        user_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, user_id)

    # Handle both UUID and non-UUID conversation IDs
    try:
        conv_uuid = uuid.UUID(conversation_id)
    except ValueError:
        # If it's not a valid UUID, generate a consistent UUID from the string
        conv_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, conversation_id)

    conversation_service = ConversationService(session)

    conversation = conversation_service.get_conversation_by_id(conv_uuid, user_uuid)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = conversation_service.get_conversation_messages(conv_uuid, user_uuid)

    return {
        "conversation_id": str(conversation.conversation_id),
        "title": conversation.title,
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat(),
        "status": conversation.status,
        "messages": [
            {
                "message_id": str(m.message_id),
                "sender_type": m.sender_type,
                "content": m.content,
                "timestamp": m.timestamp.isoformat()
            }
            for m in messages
        ]
    }