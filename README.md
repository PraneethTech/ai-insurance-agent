# Dischargo - Intelligent Discharge Analysis System

## Overview
Dischargo is a medical document management system designed to upload, analyze, and query patient discharge summaries using AI agents. It features a modern, responsive dashboard for managing files and a chat interface for specialized medical queries.

## Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS (Premium UI with Glassmorphism)
- **State Management**: React Context API
- **HTTP Client**: Axios

### Backend
- **Framework**: FastAPI
- **Database**: MongoDB (Async Motor Client)
- **Runtime**: Python 3.x

## For AI Team

### Chat Integration
The core AI logic is integrated via the chat endpoint:
- **Endpoint**: `POST /chat/{vector_id}`
- **Functionality**: Receives a user query and returns a response from one of 4 specialized agents (Bill Validator, Diet/Nutrition, Medicine Price, Discharge Summary).
- **Current State**: Mocks orchestrator logic based on keywords.

### Raw File Storage
- **Location**: `backend/data/uploads/`
- **Naming Convention**: `{upload_id}.{extension}`
- **Purpose**: Raw files stored here for the AI team to process (OCR/Vectorization).

### OCR & Extracted Content
- **Location**: `backend/data/extracted_content/`
- **Naming Convention**: `{upload_id}_extracted.txt`
- **Process**: The backend currently mocks the OCR process and saves the text to this file. The database stores the file path, not the content string.
- **UI Display**: The frontend fetches this content via `GET /uploads/{id}/extracted`.
