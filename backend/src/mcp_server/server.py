from typing import Dict, List, Any
from pydantic import BaseModel
from ..services.task_service import TaskService
from ..services.database import get_session
from sqlmodel import Session
import uuid


class TaskSchema(BaseModel):
    title: str
    description: str = ""
    completed: bool = False
    priority: str = "medium"


class MCPTool:
    def __init__(self, session: Session):
        self.session = session
        self.task_service = TaskService(session)

    def add_task(self, user_id: str, title: str, description: str = "", priority: str = "medium") -> Dict[str, Any]:
        """
        Add a new task to the user's task list.

        Args:
            user_id: The ID of the user
            title: The title of the task
            description: Optional description of the task
            priority: Priority level (low, medium, high) - defaults to medium

        Returns:
            Dictionary containing the created task information
        """
        try:
            # Handle both UUID and non-UUID user IDs
            try:
                user_uuid = uuid.UUID(user_id)
            except ValueError:
                # If it's not a valid UUID, generate a consistent UUID from the string
                user_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, user_id)

            task_data = {
                "title": title,
                "description": description,
                "priority": priority
            }

            task = self.task_service.create_task(user_uuid, task_data)

            return {
                "success": True,
                "task_id": str(task.task_id),
                "message": f"Task '{title}' added successfully",
                "task": {
                    "id": str(task.task_id),
                    "title": task.title,
                    "description": task.description,
                    "completed": task.status == "completed",
                    "priority": task.priority,
                    "created_at": task.created_at.isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to add task"
            }

    def list_tasks(self, user_id: str, status: str = "all") -> Dict[str, Any]:
        """
        List all tasks for a user, optionally filtered by status.

        Args:
            user_id: The ID of the user
            status: Filter by status ('all', 'pending', 'completed') - defaults to 'all'

        Returns:
            Dictionary containing the list of tasks
        """
        try:
            # Handle both UUID and non-UUID user IDs
            try:
                user_uuid = uuid.UUID(user_id)
            except ValueError:
                # If it's not a valid UUID, generate a consistent UUID from the string
                user_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, user_id)

            tasks = self.task_service.get_user_tasks(user_uuid, status_filter=status)

            task_list = []
            for task in tasks:
                task_list.append({
                    "id": str(task.task_id),
                    "title": task.title,
                    "description": task.description,
                    "completed": task.status == "completed",
                    "priority": task.priority,
                    "created_at": task.created_at.isoformat()
                })

            return {
                "success": True,
                "count": len(task_list),
                "tasks": task_list
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to list tasks"
            }

    def complete_task(self, user_id: str, task_id: str) -> Dict[str, Any]:
        """
        Mark a task as completed.

        Args:
            user_id: The ID of the user
            task_id: The ID of the task to complete

        Returns:
            Dictionary containing the updated task information
        """
        try:
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

            task = self.task_service.update_task_status(user_uuid, task_uuid, "completed")

            return {
                "success": True,
                "message": f"Task '{task.title}' marked as completed",
                "task": {
                    "id": str(task.task_id),
                    "title": task.title,
                    "description": task.description,
                    "completed": task.status == "completed",
                    "priority": task.priority,
                    "updated_at": task.updated_at.isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to complete task"
            }

    def update_task(self, user_id: str, task_id: str, title: str = None, description: str = None, priority: str = None) -> Dict[str, Any]:
        """
        Update an existing task.

        Args:
            user_id: The ID of the user
            task_id: The ID of the task to update
            title: New title for the task (optional)
            description: New description for the task (optional)
            priority: New priority for the task (optional)

        Returns:
            Dictionary containing the updated task information
        """
        try:
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

            update_data = {}
            if title is not None:
                update_data["title"] = title
            if description is not None:
                update_data["description"] = description
            if priority is not None:
                update_data["priority"] = priority

            task = self.task_service.update_task(user_uuid, task_uuid, update_data)

            return {
                "success": True,
                "message": f"Task '{task.title}' updated successfully",
                "task": {
                    "id": str(task.task_id),
                    "title": task.title,
                    "description": task.description,
                    "completed": task.status == "completed",
                    "priority": task.priority,
                    "updated_at": task.updated_at.isoformat()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to update task"
            }

    def delete_task(self, user_id: str, task_id: str) -> Dict[str, Any]:
        """
        Delete a task.

        Args:
            user_id: The ID of the user
            task_id: The ID of the task to delete

        Returns:
            Dictionary containing the deletion status
        """
        try:
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

            success = self.task_service.delete_task(user_uuid, task_uuid)

            if success:
                return {
                    "success": True,
                    "message": "Task deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "message": "Task not found or unauthorized"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to delete task"
            }


# For now, we'll just define the tools here. In a real MCP server, these would be served via the MCP protocol
class MCPServer:
    def __init__(self):
        self.tools = {
            "add_task": self._execute_add_task,
            "list_tasks": self._execute_list_tasks,
            "complete_task": self._execute_complete_task,
            "update_task": self._execute_update_task,
            "delete_task": self._execute_delete_task
        }

    def _execute_add_task(self, user_id: str, title: str, description: str = "", priority: str = "medium"):
        session_gen = get_session()
        session = next(session_gen)
        try:
            tool = MCPTool(session)
            return tool.add_task(user_id, title, description, priority)
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass  # Session closed properly

    def _execute_list_tasks(self, user_id: str, status: str = "all"):
        session_gen = get_session()
        session = next(session_gen)
        try:
            tool = MCPTool(session)
            return tool.list_tasks(user_id, status)
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass  # Session closed properly

    def _execute_complete_task(self, user_id: str, task_id: str):
        session_gen = get_session()
        session = next(session_gen)
        try:
            tool = MCPTool(session)
            return tool.complete_task(user_id, task_id)
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass  # Session closed properly

    def _execute_update_task(self, user_id: str, task_id: str, title: str = None, description: str = None, priority: str = None):
        session_gen = get_session()
        session = next(session_gen)
        try:
            tool = MCPTool(session)
            return tool.update_task(user_id, task_id, title, description, priority)
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass  # Session closed properly

    def _execute_delete_task(self, user_id: str, task_id: str):
        session_gen = get_session()
        session = next(session_gen)
        try:
            tool = MCPTool(session)
            return tool.delete_task(user_id, task_id)
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass  # Session closed properly

    def execute_tool(self, tool_name: str, **kwargs):
        """Execute a tool with the given parameters."""
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "message": "Unknown tool"
            }

        try:
            return self.tools[tool_name](**kwargs)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error executing tool {tool_name}"
            }


# Global MCP server instance
mcp_server = MCPServer()