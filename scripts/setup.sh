#!/bin/bash

# StudyMeet Setup Script
# This script helps you set up the project for local development

echo "🚀 Setting up StudyMeet for local development..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Error: Please run this script from the project root directory${NC}"
    exit 1
fi

echo "📦 Installing backend dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install -r requirements.txt
elif command -v pip &> /dev/null; then
    pip install -r requirements.txt
else
    echo -e "${RED}❌ Error: pip not found. Please install Python and pip first.${NC}"
    exit 1
fi

echo "📦 Installing frontend dependencies..."
cd frontend
if command -v yarn &> /dev/null; then
    yarn install
elif command -v npm &> /dev/null; then
    npm install
else
    echo -e "${RED}❌ Error: npm/yarn not found. Please install Node.js first.${NC}"
    exit 1
fi

cd ..

echo "⚙️ Setting up environment variables..."

# Create backend .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating backend .env file..."
    cat > .env << EOF
MONGO_URL=mongodb://localhost:27017
DB_NAME=studymeet_db
CORS_ORIGINS=*
EOF
    echo -e "${GREEN}✅ Created backend .env file${NC}"
else
    echo -e "${YELLOW}⚠️ Backend .env file already exists${NC}"
fi

# Create frontend .env if it doesn't exist
if [ ! -f "frontend/.env" ]; then
    echo "Creating frontend .env file..."
    cat > frontend/.env << EOF
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=443
EOF
    echo -e "${GREEN}✅ Created frontend .env file${NC}"
else
    echo -e "${YELLOW}⚠️ Frontend .env file already exists${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Start MongoDB locally (if not already running):"
echo "   - Using Docker: docker run -d -p 27017:27017 mongo"
echo "   - Using brew: brew services start mongodb-community"
echo ""
echo "2. Start the backend server:"
echo "   uvicorn backend.server:app --host 0.0.0.0 --port 8001 --reload"
echo ""
echo "3. Start the frontend (in a new terminal):"
echo "   cd frontend && npm start"
echo ""
echo "4. Open your browser to http://localhost:3000"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"