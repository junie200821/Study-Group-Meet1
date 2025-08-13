# StudyMeet - Study Group Sessions Platform

A modern, beautiful platform for creating and joining study group sessions. Built with React, FastAPI, and MongoDB.

![StudyMeet Preview](https://studymeet.preview.emergentagent.com)

## Features

- 🎨 **Beautiful Modern Design** - Gradient backgrounds and clean UI
- 👤 **Simple Authentication** - Username-based sign-in system
- 📚 **Session Management** - Create, join, and leave study sessions
- 🔍 **Search & Filter** - Find sessions by title, description, or tags
- 📈 **Trending Sessions** - See the most popular sessions
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- ⚡ **Real-time Updates** - Live participant count updates
- 🏷️ **Tagging System** - Organize sessions with custom tags

## Tech Stack

- **Frontend**: React 19, Tailwind CSS, shadcn/ui components
- **Backend**: FastAPI (Python), Serverless functions
- **Database**: MongoDB
- **Deployment**: Vercel
- **Styling**: Modern gradients, animations, and responsive design

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd studymeet
   ```

2. **Install dependencies**
   ```bash
   # Frontend dependencies
   cd frontend
   npm install
   
   # Backend dependencies  
   cd ..
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create frontend/.env
   REACT_APP_BACKEND_URL=http://localhost:8001
   
   # Create .env in root
   MONGO_URL=mongodb://localhost:27017
   DB_NAME=studymeet_db
   ```

4. **Run the application**
   ```bash
   # Start backend (from root)
   uvicorn backend.server:app --host 0.0.0.0 --port 8001 --reload
   
   # Start frontend (in new terminal)
   cd frontend
   npm start
   ```

## Deploy to Vercel

### Option 1: Deploy via Vercel Dashboard

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will auto-detect the configuration

3. **Set Environment Variables**
   In Vercel dashboard, add:
   ```
   MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/
   DB_NAME=studymeet_db
   ```

### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Login and deploy**
   ```bash
   vercel login
   vercel --prod
   ```

3. **Set environment variables**
   ```bash
   vercel env add MONGO_URL
   vercel env add DB_NAME
   ```

## Database Setup

### MongoDB Atlas (Recommended for Production)

1. **Create MongoDB Atlas Account**
   - Go to [mongodb.com/atlas](https://mongodb.com/atlas)
   - Create a free cluster

2. **Get Connection String**
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your database password

3. **Whitelist IP Addresses**
   - In Network Access, add `0.0.0.0/0` for Vercel deployment
   - Or add specific IP ranges for better security

### Local MongoDB (Development)

```bash
# Install MongoDB locally
brew install mongodb/brew/mongodb-community  # macOS
# or use Docker
docker run -d -p 27017:27017 mongo
```

## Environment Variables

### Frontend (.env)
```env
REACT_APP_BACKEND_URL=https://your-vercel-app.vercel.app
```

### Backend (Vercel Environment Variables)
```env
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/studymeet_db
DB_NAME=studymeet_db
```

## Project Structure

```
studymeet/
├── api/                    # Vercel serverless functions
│   ├── auth.py            # Authentication endpoints
│   ├── sessions.py        # Session management endpoints
│   └── health.py          # Health check endpoint
├── frontend/              # React application
│   ├── src/
│   │   ├── components/ui/ # shadcn/ui components
│   │   ├── App.js        # Main React component
│   │   └── App.css       # Styling
│   └── package.json
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/auth/login` - User authentication
- `GET /api/sessions` - Get all sessions
- `POST /api/sessions` - Create new session
- `GET /api/sessions/trending` - Get trending sessions
- `POST /api/sessions/{id}/join` - Join session
- `POST /api/sessions/{id}/leave` - Leave session
- `DELETE /api/sessions/{id}` - Delete session

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

If you have any questions or need help with deployment, please open an issue on GitHub.

---

**Built with ❤️ for collaborative learning**
