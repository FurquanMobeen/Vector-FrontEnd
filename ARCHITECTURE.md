# Three-Service Architecture

This project uses a microservices architecture with three separate services:

## Services Overview

```
┌─────────────────┐
│   Frontend      │  Next.js 15 + TypeScript
│  (This Repo)    │  Port: 3000
└────────┬────────┘
         │
         ├──────────────────┐
         │                  │
         ▼                  ▼
┌─────────────────┐  ┌──────────────────┐
│  Auth Backend   │  │ Vector Search    │
│                 │  │   Backend        │
│  Port: 8000     │  │  Port: 8001      │
└─────────────────┘  └──────────────────┘
```

## 1. Frontend (This Repository)

**Technology**: Next.js 15, TypeScript, Tailwind CSS, shadcn/ui

**Responsibilities**:
- User interface
- Client-side routing
- State management
- API client calls to both backends

**Key Files**:
- `lib/api.ts` - Auth API client
- `vector-search/api/client.ts` - Vector Search API client
- `components/` - Reusable UI components
- `app/` - Pages and layouts

**Environment Variables**:
```env
NEXT_PUBLIC_AUTH_API_URL=http://localhost:8000
NEXT_PUBLIC_VECTOR_SEARCH_API_URL=http://localhost:8001
```

## 2. Auth Backend (Separate Repository)

**Technology**: FastAPI (Python)

**Responsibilities**:
- User authentication (login/logout)
- JWT token management
- User profile management
- Session handling

**Required Endpoints**:
```
POST /api/auth/login
GET  /api/auth/me
```

**Suggested Structure**:
```
auth-backend/
├── app/
│   ├── main.py
│   ├── auth/
│   │   ├── routes.py
│   │   ├── models.py
│   │   └── utils.py
│   └── database/
├── requirements.txt
└── .env
```

## 3. Vector Search Backend (Separate Repository)

**Technology**: FastAPI (Python) + CLIP Model + ChromaDB

**Responsibilities**:
- CLIP model inference
- Vector embeddings generation
- Image similarity search
- Text-to-image search
- Image storage and metadata management
- ChromaDB vector database operations

**Required Endpoints**:
```
POST   /api/search/image        # Upload image, get similar images
POST   /api/search/text         # Text query, get matching images
GET    /api/images              # List all images
POST   /api/images              # Upload new image
PUT    /api/images/{path}/metadata  # Update image metadata
DELETE /api/images/{path}       # Delete image
GET    /api/images/metadata/export  # Export metadata
GET    /static/{path}           # Serve static images
```

**Suggested Structure**:
```
vector-search-backend/
├── app/
│   ├── main.py
│   ├── routes/
│   │   ├── search.py
│   │   └── images.py
│   ├── services/
│   │   ├── clip_service.py      # CLIP model logic
│   │   ├── vector_db.py         # ChromaDB operations
│   │   └── image_processor.py   # Image handling
│   ├── models/
│   │   └── schemas.py
│   └── config.py
├── data/                         # Image storage
├── embedded_data/                # ChromaDB storage
├── requirements.txt
└── .env
```

**Key Dependencies**:
```
fastapi
uvicorn
transformers
torch
pillow
chromadb
python-multipart
```

## Frontend Client Code

### Auth API Client ([lib/api.ts](lib/api.ts))
```typescript
// Calls to http://localhost:8000
- login(credentials)
- getCurrentUser()
```

### Vector Search API Client ([vector-search/api/client.ts](vector-search/api/client.ts))
```typescript
// Calls to http://localhost:8001
- searchByImage(image)
- searchByText(query)
- getAllImages()
- uploadImage(data)
- updateMetadata(data)
- deleteImage(path)
- exportMetadata(path)
```

## Development Setup

### 1. Start Auth Backend
```bash
cd auth-backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Start Vector Search Backend
```bash
cd vector-search-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### 3. Start Frontend
```bash
cd Vector-FrontEnd
npm install
npm run dev
```

## Production Deployment

### Frontend
- **Platform**: Vercel, Netlify, or any Node.js hosting
- **Build**: `npm run build`
- **Environment Variables**: Set in platform dashboard

### Auth Backend
- **Platform**: Railway, Render, Fly.io, AWS Lambda, etc.
- **Container**: Docker recommended
- **URL**: Update `NEXT_PUBLIC_AUTH_API_URL`

### Vector Search Backend
- **Platform**: Railway, Render, AWS EC2 (needs GPU for faster inference)
- **Container**: Docker recommended
- **Storage**: Persistent volume for images and ChromaDB
- **URL**: Update `NEXT_PUBLIC_VECTOR_SEARCH_API_URL`

## CORS Configuration

Both backends need CORS configured to allow requests from the frontend:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Authentication Flow

1. User logs in via frontend
2. Frontend calls Auth Backend (`POST /api/auth/login`)
3. Auth Backend returns JWT token
4. Frontend stores token in localStorage
5. All subsequent requests include `Authorization: Bearer <token>` header
6. Both backends validate JWT tokens

## Moving Python Code to Backend

The following Python files should be moved to the **Vector Search Backend**:

**From current repo to vector-search-backend:**
- `src/image_search.py` → `app/services/clip_service.py`
- `embed_images.py` → `app/services/embed_images.py`
- `download_data.py` → `scripts/download_data.py`
- `embedded_data/` → `embedded_data/` (ChromaDB data)
- `data/` → `data/` (image files)

**Keep for reference:**
- `src/rebuild_db_on_deploy.py` → Backend deployment script
- `src/generate_password_hash.py` → Auth backend utility

## Benefits of This Architecture

1. **Scalability**: Each service scales independently
2. **Separation of Concerns**: Clear boundaries between services
3. **Technology Flexibility**: Each service uses optimal tech stack
4. **Independent Deployment**: Deploy each service separately
5. **Reusability**: Multiple frontends can use same backends
6. **Cost Efficiency**: Vector search on GPU instance, others on cheaper infrastructure

## Next Steps

1. Create two new repositories:
   - `auth-backend`
   - `vector-search-backend`

2. Implement the FastAPI endpoints as documented above

3. Move Python code from this repo to appropriate backend

4. Test locally with all three services running

5. Deploy to production platforms

6. Update environment variables with production URLs
