from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Dict, Any
from ..services.database import get_session
from ..mcp_server.server import mcp_server
import uuid

router = APIRouter()


@router.get("/mcp/tools")
def list_mcp_tools():
    """
    List all available MCP tools.
    """
    available_tools = list(mcp_server.tools.keys())
    return {
        "tools": available_tools,
        "count": len(available_tools),
        "description": "Available MCP tools for task management"
    }


@router.post("/mcp/tools/{tool_name}")
def execute_mcp_tool(
    tool_name: str,
    params: Dict[str, Any],
    session: Session = Depends(get_session)
):
    """
    Execute an MCP tool directly via HTTP endpoint.
    This allows direct access to MCP tools for programmatic use.
    """
    # Extract user_id from params - it's required for all tools
    user_id = params.get('user_id')
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    # Validate user_id format - handle both UUID and non-UUID formats
    try:
        uuid.UUID(user_id)
    except ValueError:
        # If it's not a valid UUID, we'll convert it to UUID in the tool execution
        # This is fine, as our MCP tools can handle both formats
        pass  # Allow both UUID and non-UUID formats

    # Remove user_id from params since we'll pass it separately
    tool_params = {k: v for k, v in params.items() if k != 'user_id'}

    # Execute the tool
    result = mcp_server.execute_tool(tool_name, user_id=user_id, **tool_params)

    if not result['success']:
        status_code = 404 if 'not found' in result.get('message', '').lower() else 400
        raise HTTPException(status_code=status_code, detail=result.get('message', 'Tool execution failed'))

    return result