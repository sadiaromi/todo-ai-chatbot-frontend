'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/navigation';
import { useSession, signOut } from '../lib/auth-react';
import apiService from '../services/api';

// Dynamically import the ChatInterface component with no SSR
const ChatInterface = dynamic(
  () => import('./ChatInterface'),
  {
    ssr: false,
    loading: () => (
      <div className="h-full flex flex-col">
        <div className="flex-1 overflow-y-auto p-4">
          <div className="message assistant-message mb-4 p-3 rounded-lg bg-gray-100 max-w-[80%]">
            <div className="message-content">Loading chat interface...</div>
            <div className="message-role text-xs text-gray-500">AI Assistant</div>
          </div>
        </div>
        <div className="p-4 border-t border-gray-200">
          <div className="flex space-x-2">
            <input
              value=""
              placeholder="Type your message here..."
              disabled={true}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md disabled:opacity-50"
            />
            <button disabled={true} className="px-4 py-2 bg-blue-500 text-white rounded-md disabled:opacity-50">
              Send
            </button>
          </div>
        </div>
      </div>
    )
  }
);

type Task = {
  task_id: string;
  title: string;
  description?: string;
  status: string;
  priority: string;
  created_at: string;
  updated_at: string;
  completed_at?: string | null;
};

export default function Dashboard() {
  const { data: session, isLoading: sessionLoading } = useSession();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(true);
  const router = useRouter();

  // Fetch tasks for the current user
  const fetchTasks = async () => {
    try {
      if (session?.user?.id) {
        const response = await apiService.getUserTasks(session.user.id);
        setTasks(response.tasks || []);
      }
    } catch (error) {
      console.error('Error fetching tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  // Watch session and redirect if not logged in
  useEffect(() => {
    if (sessionLoading) return;

    if (!session?.user) {
      router.push('/login');
    } else {
      fetchTasks();
    }
  }, [session, sessionLoading, router]);

  if (sessionLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Checking authentication...</p>
        </div>
      </div>
    );
  }

  if (!session?.user) return null;

  const pendingTasks = tasks.filter(task => task.status !== 'completed');
  const completedTasks = tasks.filter(task => task.status === 'completed');

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Main Content */}
      <div className={`flex-1 transition-all duration-300 ${sidebarOpen ? 'md:mr-80' : ''}`}>
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Todo AI Chatbot</h1>
              <p className="mt-1 text-sm text-gray-500">Manage your tasks with natural language</p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="md:hidden text-gray-600 hover:text-gray-900"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <button
                onClick={async () => {
                  try {
                    await signOut();
                    router.push('/login');
                  } catch (error) {
                    console.error('Logout error:', error);
                    router.push('/login');
                  }
                }}
                className="text-sm text-blue-600 hover:text-blue-800 font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          {/* Task Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center">
                <div className="p-3 rounded-full bg-blue-100 mr-4">
                  <p className="text-2xl font-semibold text-gray-900">{tasks.length}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Tasks</p>
                </div>
              </div>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center">
                <div className="p-3 rounded-full bg-yellow-100 mr-4">
                  <p className="text-2xl font-semibold text-gray-900">{pendingTasks.length}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600">Pending</p>
                </div>
              </div>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center">
                <div className="p-3 rounded-full bg-green-100 mr-4">
                  <p className="text-2xl font-semibold text-gray-900">{completedTasks.length}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600">Completed</p>
                </div>
              </div>
            </div>
          </div>

          {/* Task Board */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Pending Tasks */}
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Pending Tasks</h2>
              <div className="space-y-4">
                {loading ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                  </div>
                ) : pendingTasks.length > 0 ? (
                  pendingTasks.map(task => (
                    <div key={task.task_id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="font-medium text-gray-900">{task.title}</h3>
                          {task.description && <p className="text-sm text-gray-500 mt-1">{task.description}</p>}
                          <p className="text-xs text-gray-400 mt-2">
                            Created: {new Date(task.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          task.priority === 'high' ? 'bg-red-100 text-red-800' :
                          task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {task.priority}
                        </span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <p>No pending tasks. Great job!</p>
                  </div>
                )}
              </div>
            </div>

            {/* Completed Tasks */}
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Completed Tasks</h2>
              <div className="space-y-4">
                {loading ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                  </div>
                ) : completedTasks.length > 0 ? (
                  completedTasks.map(task => (
                    <div key={task.task_id} className="border border-gray-200 rounded-lg p-4 opacity-75">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="font-medium text-gray-900 line-through">{task.title}</h3>
                          {task.description && <p className="text-sm text-gray-500 mt-1 line-through">{task.description}</p>}
                          <p className="text-xs text-gray-400 mt-2">
                            Completed: {task.completed_at ? new Date(task.completed_at).toLocaleDateString() : 'N/A'}
                          </p>
                        </div>
                        <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800">completed</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <p>No completed tasks yet. Keep going!</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>

      {/* AI Chatbot Sidebar */}
      <div className={`fixed inset-y-0 right-0 w-80 bg-white shadow-xl transform transition-transform duration-300 ease-in-out z-10 ${
        sidebarOpen ? 'translate-x-0' : 'translate-x-full'
      } md:translate-x-0 md:static md:w-80 md:flex md:flex-col`}>
        <div className="p-4 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-lg font-semibold text-gray-900">AI Assistant</h2>
          <button
            onClick={() => setSidebarOpen(false)}
            className="text-gray-500 hover:text-gray-700 md:hidden"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
        <div className="flex-1 overflow-hidden flex flex-col">
          {/* Pass fetchTasks as onTaskUpdate to ChatInterface */}
          <ChatInterface onTaskUpdate={fetchTasks} />
        </div>
      </div>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-0 md:hidden"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}
    </div>
  );
}
