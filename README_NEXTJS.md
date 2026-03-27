# CLIP Vector Search - Next.js Frontend

A modern, TypeScript-based web application for AI-powered image search using CLIP embeddings. Built with Next.js 15, shadcn/ui, and Tailwind CSS.

## Features

- **Image Search**: Upload an image to find visually similar images
- **Text Search**: Search for images using natural language descriptions
- **Image Management**: Upload, edit metadata, and delete images
- **Authentication**: Secure login with JWT tokens
- **Modern UI**: Dark theme with purple/pink gradient accents
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **UI Components**: shadcn/ui (Radix UI primitives)
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **Form Handling**: React Hook Form + Zod

## Prerequisites

- Node.js 18+ and npm
- FastAPI backend running at `http://localhost:8000` (see Backend Requirements section)

## Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Set up environment variables**:
   The `.env.local` file is already configured with:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Run development server**:
   ```bash
   npm run dev
   ```

4. **Open the application**:
   Navigate to [http://localhost:3000](http://localhost:3000)

## Available Scripts

- `npm run dev` - Start development server (port 3000)
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

## Backend Requirements

**IMPORTANT**: This frontend requires a FastAPI backend with the following endpoints:

### Authentication
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Search
- `POST /api/search/image` - Search by uploaded image
  - Accepts: `multipart/form-data` with `image` file
  - Returns: Array of search results with similarity scores

- `POST /api/search/text` - Search by text query
  - Accepts: `{ query: string }`
  - Returns: Array of search results with similarity scores

### Image Management
- `GET /api/images` - Get all images with metadata
  - Returns: `[{ path: string, title: string, description: string }]`

- `POST /api/images` - Upload new image
  - Accepts: `multipart/form-data` with `image`, `title`, `description`
  - Returns: Success message

- `PUT /api/images/{image_path}/metadata` - Update image metadata
  - Accepts: `{ title: string, description: string }`
  - Returns: Success message

- `DELETE /api/images/{image_path}` - Delete image
  - Returns: Success message

- `GET /api/images/metadata/export` - Export metadata as JSON
  - Optional query param: `image_path` for single image
  - Returns: JSON metadata

### Static Files
- Images should be served at `/static/{image_path}`

## Project Structure

```
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Authentication routes
│   │   └── login/                # Login page
│   ├── (dashboard)/              # Protected dashboard routes
│   │   ├── image-search/         # Image search page
│   │   ├── text-search/          # Text search page
│   │   ├── manage-images/        # Image management page
│   │   ├── layout.tsx            # Dashboard layout with sidebar
│   │   └── page.tsx              # Home page
│   ├── layout.tsx                # Root layout
│   └── globals.css               # Global styles
├── components/                   # React components
│   ├── ui/                       # shadcn/ui components
│   ├── AuthProvider.tsx          # Authentication context
│   ├── ImageGrid.tsx             # Image grid display
│   ├── ImageRotator.tsx          # Image rotation controls
│   ├── Pagination.tsx            # Pagination component
│   └── Sidebar.tsx               # Navigation sidebar
├── lib/                          # Utility functions
│   ├── api.ts                    # API client (Axios)
│   ├── auth.ts                   # Auth helper functions
│   ├── types.ts                  # TypeScript interfaces
│   └── utils.ts                  # Utility functions
└── public/                       # Static assets
```

## Authentication

The application uses JWT token authentication:
1. Login credentials are sent to `/api/auth/login`
2. JWT token is stored in `localStorage`
3. Token is automatically included in all API requests via Axios interceptor
4. Protected routes redirect to login if unauthenticated

Default test credentials:
- Username: `admin`
- Password: `admin123`

## Pages

### Login (`/login`)
- Center-aligned login form
- Username and password inputs
- Error handling with user-friendly messages
- Test credentials displayed for easy access

### Home (`/`)
- Three feature cards: Image Search, Text Search, Manage Images
- Each card links to its respective page
- Gradient accents with hover effects
- "How it works" information section

### Image Search (`/image-search`)
- Upload image via file picker
- Image rotation controls (90° left/right, reset)
- Search button to find similar images
- Results displayed in 3x3 grid
- Pagination (9 results per page)
- Similarity scores shown for each result

### Text Search (`/text-search`)
- Text area for entering search query
- Example queries for quick testing
- Ctrl+Enter shortcut to search
- Results displayed in 3x3 grid
- Pagination (9 results per page)

### Manage Images (`/manage-images`)
**Upload Section**:
- Choose image file
- Rotation controls
- Title and description inputs
- Add to database

**Manage Section**:
- Search/filter images by title
- Select image from list
- Edit metadata (title, description)
- Delete image with confirmation dialog
- Image preview with metadata display

**Export Section**:
- Export all images metadata
- Export selected image metadata only
- Download as JSON file

## Customization

### Theme Colors
Edit `tailwind.config.ts` to customize the purple/pink gradient theme:
- `primary`: #a855f7 (purple)
- `secondary`: #ec4899 (pink)
- `background`: #0f0f0f (dark)
- `sidebar`: #1a1a1a (darker gray)

### API URL
Change the backend URL in `.env.local`:
```
NEXT_PUBLIC_API_URL=http://your-backend-url
```

## Troubleshooting

### Build Errors
- Run `npm install` to ensure all dependencies are installed
- Check that all TypeScript files compile: `npx tsc --noEmit`

### API Connection Errors
- Ensure the FastAPI backend is running at `http://localhost:8000`
- Check browser console for CORS errors
- Verify backend endpoints match the expected API structure

### Image Loading Issues
- Ensure images are served from backend at `/static/{path}`
- Check browser console for 404 errors
- Verify image paths in the database are correct

## Production Deployment

1. **Build the application**:
   ```bash
   npm run build
   ```

2. **Start production server**:
   ```bash
   npm start
   ```

3. **Environment variables**:
   - Update `NEXT_PUBLIC_API_URL` to point to your production backend
   - Consider using environment-specific `.env.production` file

4. **Deployment platforms**:
   - Vercel (recommended for Next.js)
   - Netlify
   - Docker container
   - Node.js server

## Migration from Streamlit

This Next.js application replaces the previous Streamlit frontend with feature parity:
- ✅ All pages migrated (Login, Home, Image Search, Text Search, Manage Images)
- ✅ Image rotation functionality preserved
- ✅ Pagination implemented
- ✅ Metadata management (edit, delete, export)
- ✅ Authentication with JWT tokens
- ✅ Dark theme with purple/pink gradients

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

See LICENSE file for details.

## Author

By Furquan Mobeen
