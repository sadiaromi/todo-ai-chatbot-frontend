import { useSession } from '../lib/auth-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://roman-sadia-todo-ai-chatbot-backend.hf.space';

class BetterAuthApiService {
  baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async request(endpoint: string, options: RequestInit = {}) {
    // Get session token from Better Auth
    const session = await this.getSession();
    const token = session?.user?.id; // Use user ID as the identifier

    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    } as Record<string, string>;

    // Add auth token if available
    if (token && !headers['Authorization']) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const config: RequestInit = {
      headers,
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
      if (error instanceof TypeError && (error as TypeError).message.includes('fetch')) {
        throw new Error('Network error: Unable to connect to the server. Please make sure the backend server is running on ' + this.baseURL);
      }
      throw error;
    }
  }

  // Helper to get session (would normally use the session context)
  private async getSession(): Promise<{user?: {id: string}} | null> {
    try {
      // This is a simplified approach - in practice, you'd use the session context
      const response = await fetch('/api/auth/get-session');
      if (response.ok) {
        return await response.json();
      }
      return null;
    } catch (error) {
      console.error('Failed to get session:', error);
      return null;
    }
  }

  // Authentication methods
  async login(email: string, password: string) {
    // This would be handled by Better Auth's sign-in
    // We'll use the API directly here
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async register(email: string, password: string, username: string) {
    // This would be handled by Better Auth's sign-up
    // We'll use the API directly here
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, username }),
    });
  }

  // Chat methods
  async sendMessage(userId: string, message: string, conversationId: string | null = null) {
    return this.request(`/api/${userId}/chat`, {
      method: 'POST',
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });
  }

  async getUserConversations(userId: string, params: Record<string, string> = {}) {
    const queryParams = new URLSearchParams(params);
    return this.request(`/api/${userId}/conversations?${queryParams}`);
  }

  async getConversationDetails(userId: string, conversationId: string) {
    return this.request(`/api/${userId}/conversations/${conversationId}`);
  }

  // Task methods
  async getUserTasks(userId: string, status: string = 'all') {
    return this.request(`/api/${userId}/tasks?status=${status}`);
  }

  async createTask(userId: string, taskData: Record<string, any>) {
    return this.request(`/api/${userId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  }

  async updateTask(userId: string, taskId: string, taskData: Record<string, any>) {
    return this.request(`/api/${userId}/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(taskData),
    });
  }

  async deleteTask(userId: string, taskId: string) {
    return this.request(`/api/${userId}/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }
}

export default new BetterAuthApiService();