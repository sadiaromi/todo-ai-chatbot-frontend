const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://roman-sadia-todo-ai-chatbot-backend.hf.space';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorData}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Network error: Unable to connect to the server. Please make sure the backend server is running on ' + this.baseURL);
      }
      throw error;
    }
  }

  // Chat methods
  async sendMessage(userId, message, conversationId = null) {
    // Use a proper UUID format for the user ID to match backend expectations
    const actualUserId = userId || '123e4567-e89b-12d3-a456-426614174000'; // demo user UUID
    return this.request(`/api/${actualUserId}/chat`, {
      method: 'POST',
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });
  }

  async getUserConversations(userId, params = {}) {
    const actualUserId = userId || '123e4567-e89b-12d3-a456-426614174000'; // demo user UUID
    const queryParams = new URLSearchParams(params);
    return this.request(`/api/${actualUserId}/conversations?${queryParams}`);
  }

  async getConversationDetails(userId, conversationId) {
    const actualUserId = userId || '123e4567-e89b-12d3-a456-426614174000'; // demo user UUID
    return this.request(`/api/${actualUserId}/conversations/${conversationId}`);
  }

  // Task methods
  async getUserTasks(userId, status = 'all') {
    // Use a proper UUID format for the user ID to match backend expectations
    const actualUserId = userId || '123e4567-e89b-12d3-a456-426614174000'; // demo user UUID
    return this.request(`/api/${actualUserId}/tasks?status=${status}`);
  }

  async createTask(userId, taskData) {
    const actualUserId = userId || '123e4567-e89b-12d3-a456-426614174000'; // demo user UUID
    return this.request(`/api/${actualUserId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  }

  async updateTask(userId, taskId, taskData) {
    const actualUserId = userId || '123e4567-e89b-12d3-a456-426614174000'; // demo user UUID
    return this.request(`/api/${actualUserId}/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(taskData),
    });
  }

  async deleteTask(userId, taskId) {
    const actualUserId = userId || '123e4567-e89b-12d3-a456-426614174000'; // demo user UUID
    return this.request(`/api/${actualUserId}/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }

  // MCP Tools methods
  async listMcpTools() {
    return this.request('/mcp/tools', {
      method: 'GET',
    });
  }

  async executeMcpTool(toolName, params) {
    return this.request(`/mcp/tools/${toolName}`, {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }
}

export default new ApiService();