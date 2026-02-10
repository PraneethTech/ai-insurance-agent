# 🚀 Quick Start Guide - Discharge Agent System

## Prerequisites Checklist

- [ ] MongoDB installed and running on `mongodb://localhost:27017`
- [ ] Python 3.8+ installed
- [ ] Node.js 18+ installed

## Step 1: Start Backend (FastAPI)

```bash
cd backend

# Create virtual environment (first time only)
python -m venv backendenv

# Activate virtual environment
# Windows:
backendenv\Scripts\activate
# Linux/Mac:
source backendenv/bin/activate

# Install dependencies (first time only)
pip install -r app/requirements.txt

# Start server
python -m uvicorn app.main:app --reload
```

✅ Backend running on: `http://localhost:8000`
✅ Swagger docs: `http://localhost:8000/docs`

## Step 2: Start Frontend (Next.js)

Open a new terminal:

```bash
cd frontend

# Dependencies already installed ✅

# Start development server
npm run dev
```

✅ Frontend running on: `http://localhost:3000`

## Step 3: Test the Application

### 1. Register a User
1. Go to `http://localhost:3000`
2. Click "Sign up"
3. Fill in all fields
4. Submit

### 2. Login
1. Use your credentials
2. You'll be redirected to dashboard

### 3. Upload a Document
1. Click "Upload Document" in sidebar
2. Drag & drop any file (PDF, JPG, etc.)
3. Add description: "Test discharge summary"
4. Click "Upload Document"

### 4. View Files
1. Click "All Files" in sidebar
2. See your uploaded file card
3. Click the card

### 5. Chat with AI
1. In the file detail view, see 60/40 split
2. Left: File details & extracted content
3. Right: Chat interface
4. Try these questions:
   - "What bills are included?" → Bill Validator Agent
   - "What diet should I follow?" → Diet & Nutrition Agent
   - "Show medication prices" → Medicine Price Comparison Agent
   - "Summarize the discharge" → Discharge Summary Agent

## Endpoints Available

### Authentication
- `POST /auth/register` - Create account
- `POST /auth/login` - Get JWT token

### File Management
- `POST /uploads/` - Upload file
- `GET /uploads/` - List your files
- `GET /uploads/{id}` - Get file details

### Chat
- `POST /chat/{vector_id}` - Chat with AI agents

## Troubleshooting

### Backend Issues

**MongoDB Connection Error:**
```bash
# Make sure MongoDB is running
mongod --dbpath <path-to-data-directory>
```

**Port 8000 already in use:**
```bash
# Use different port
uvicorn app.main:app --reload --port 8001
```

### Frontend Issues

**Port 3000 already in use:**
```bash
# Next.js will ask if you want to use 3001, type 'y'
```

**Module not found:**
```bash
# Re-install dependencies
rm -rf node_modules package-lock.json
npm install
```

**Cannot connect to backend:**
- Check `.env.local` has: `NEXT_PUBLIC_API_URL=http://localhost:8000`
- Make sure backend is running

## Architecture Overview

```
User Browser (localhost:3000)
    ↓
Next.js Frontend
    ↓
API Client (axios with JWT)
    ↓
FastAPI Backend (localhost:8000)
    ↓
MongoDB (localhost:27017)
    ├── users collection
    └── uploads collection
```

## What's Mocked (For AI Team to Replace)

1. **OCR Processing** - Currently returns mock extracted content
2. **Vector Embeddings** - Generates mock vector_id (e.g., `vec_a1b2c3d4`)
3. **Agent Responses** - Keyword-based routing with mock responses
4. **File Storage** - Only path stored, not actual file

## Ready for Production?

✅ Frontend fully functional
✅ Backend API complete
✅ Authentication working
✅ File upload working
✅ Chat interface ready

🔄 Need real implementations:
- OCR service integration
- Vector database (Pinecone, Weaviate, etc.)
- Real agent logic from AI team
- File storage (S3, Azure Blob, etc.)

---

**Questions?** Check the [walkthrough.md](file:///C:/Users/saipraneeth/.gemini/antigravity/brain/0f988d22-e92e-4277-add3-566b59a1f5c9/walkthrough.md) for detailed implementation info.

Happy coding! 🎉
