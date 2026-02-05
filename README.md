# Todo AI Chatbot Frontend

AI-Powered Todo Web Application with natural language task management, authentication, and modern dashboard UI. This is the frontend for the Todo AI Chatbot application that connects to a backend deployed on Hugging Face Spaces.

## 🚀 Features

- **Authentication System**: Secure login/signup with JWT tokens
- **Natural Language Processing**: AI chatbot understands task commands
- **Real-time Dashboard**: Task board with pending/completed tasks
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Clean, professional SaaS-style interface
- **Hugging Face Backend**: Connects to AI backend deployed on Hugging Face Spaces

## 🛠️ Tech Stack

### Frontend
- **Next.js** (App Router)
- **React** (Client Components)
- **Tailwind CSS** (Styling)
- **TypeScript**

## 🚦 Getting Started

### Prerequisites

- Node.js 18+

### Installation

1. Clone the repository:
```bash
git clone https://github.com/sadiaromi/todo-ai-chatbot-frontend.git
```

2. Navigate to the project directory:
```bash
cd todo-ai-chatbot-frontend
```

3. Install dependencies:
```bash
npm install
```

4. Create environment file:
```bash
cp .env.example .env.local
```

5. Update `.env.local` with your backend API URL:
```bash
NEXT_PUBLIC_API_BASE_URL=https://your-hf-space-url.hf.space
```

### Running the Application

1. Development mode:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## 🤖 AI Chatbot Capabilities

The AI chatbot understands various commands:

### Adding Tasks
- "Add a task to buy groceries"
- "Create a new task for calling mom"
- "Make a todo for project deadline"

### Listing Tasks
- "Show my tasks"
- "What do I have pending?"
- "List completed tasks"

### Completing Tasks
- "Mark task 1 as complete"
- "Complete the grocery task"
- "Check off item 3"

### Updating Tasks
- "Update task 1 to call dad instead"
- "Change the priority of task 2"

### Deleting Tasks
- "Delete the old task"
- "Remove task 3"

## 🔐 Authentication Flow

1. **Login/Signup**: Users authenticate via Better Auth email/password
2. **Session Management**: Better Auth handles sessions with secure cookies
3. **Protected Routes**: Unauthenticated users redirected to login
4. **API Authentication**: User ID from Better Auth session passed to backend API
5. **Logout**: Secure session termination via Better Auth

## 🌐 Backend Connection

This frontend connects to a backend deployed on Hugging Face Spaces at:
- Backend URL: `https://roman-sadia-todo-ai-chatbot-backend.hf.space`

## 🚢 Deployment

### Vercel Deployment

This application is optimized for Vercel deployment:

1. Go to [Vercel](https://vercel.com)
2. Import this GitHub repository
3. Add environment variable:
   - `NEXT_PUBLIC_API_BASE_URL`: Your backend API URL
4. Deploy

### Environment Variables

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_BASE_URL=https://your-hf-space-url.hf.space
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Run tests (`npm test`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, please open an issue in the GitHub repository.

## 🛠️ Tech Stack

### Frontend
- **Next.js** (App Router)
- **React** (Client Components)
- **Tailwind CSS** (Styling)
- **TypeScript**

### Backend
- **FastAPI** (Web Framework)
- **SQLModel** (ORM)
- **OpenAI Agents SDK** (AI Integration)
- **Official MCP SDK** (Model Context Protocol)

### Database
- **PostgreSQL** (Neon Serverless)

## 🏗️ Project Structure

```
todo-ai-chatbot/
├── app/                     # Next.js app router
│   ├── login/              # Login page
│   ├── signup/             # Signup page
│   └── page.tsx            # Dashboard page
├── src/
│   ├── components/         # React components
│   │   ├── Dashboard.jsx   # Main dashboard UI
│   │   └── ChatInterface.jsx # AI chat interface
│   └── services/           # API services
│       └── api.js          # API client
├── backend/
│   ├── src/
│   │   ├── api/            # API routes
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── mcp_server/     # MCP server implementation
├── specs/                  # Specification documents
│   ├── agent.spec.md       # AI agent specifications
│   └── mcp-tools.spec.md   # MCP tools specifications
└── README.md
```

## 🚦 Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL (or Docker for local development)
- OpenAI API key

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your configuration
```

### Frontend Setup

1. Navigate back to project root:
```bash
cd ..
```

2. Install frontend dependencies:
```bash
npm install
```

3. Create frontend environment file:
```bash
# Create .env.local in project root
echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" > .env.local
```

### Database Setup

For local development, the application uses SQLite by default. For production, configure PostgreSQL in your `.env` file:

```bash
DATABASE_URL=postgresql://username:password@localhost:5432/todo_chatbot
```

To initialize the database:
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

### Environment Variables

#### Backend (.env)
```bash
DATABASE_URL=sqlite:///./todo_chatbot.db
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=your-openai-api-key-here
```

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## ▶️ Running the Application

### Development Mode

Terminal 1 - Start the backend:
```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - Start the frontend:
```bash
npm run dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Backend API Docs: http://localhost:8000/docs

### Using Docker Compose
```bash
docker-compose up --build
```

## 🧠 AI Architecture

### MCP Server
The application implements an Official MCP SDK server exposing the following tools:

- `add_task`: Create new tasks
- `list_tasks`: Retrieve user's tasks
- `complete_task`: Mark tasks as complete
- `update_task`: Modify task properties
- `delete_task`: Remove tasks

### Natural Language Commands
The AI chatbot understands various commands:

#### Adding Tasks
- "Add a task to buy groceries"
- "Create a new task for calling mom"
- "Make a todo for project deadline"

#### Listing Tasks
- "Show my tasks"
- "What do I have pending?"
- "List completed tasks"

#### Completing Tasks
- "Mark task 1 as complete"
- "Complete the grocery task"
- "Check off item 3"

#### Updating Tasks
- "Update task 1 to call dad instead"
- "Change the priority of task 2"

#### Deleting Tasks
- "Delete the old task"
- "Remove task 3"

## 🔐 Authentication Flow

1. **Login/Signup**: Users authenticate via Better Auth email/password
2. **Session Management**: Better Auth handles sessions with secure cookies
3. **Protected Routes**: Unauthenticated users redirected to login
4. **API Authentication**: User ID from Better Auth session passed to backend API
5. **Logout**: Secure session termination via Better Auth

## 📊 Database Schema

### Task Model
- id (UUID)
- user_id (UUID, foreign key)
- title (string)
- description (string, optional)
- completed (boolean)
- priority (enum: low, medium, high)
- created_at (datetime)
- updated_at (datetime)

### User Model
- id (UUID)
- email (string)
- password_hash (string)
- created_at (datetime)

### Conversation Model
- id (UUID)
- user_id (UUID, foreign key)
- created_at (datetime)
- updated_at (datetime)

### Message Model
- id (UUID)
- conversation_id (UUID, foreign key)
- role (enum: user, assistant)
- content (text)
- created_at (datetime)

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest
```

### Frontend Tests
```bash
npm run test
```

## 🚢 Deployment

### Production Build
```bash
# Frontend
npm run build

# Backend
# Configure production database and environment variables
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Run tests (`npm test` and `python -m pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, please open an issue in the GitHub repository.