export interface User {
  username: string;
  full_name: string;
  role: string;
  email?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface ApiError {
  message: string;
  detail?: string;
}

export interface SearchResult {
  path: string;
  title: string;
  description: string;
  similarity: number;
  caption?: string;
}

export interface ImageMetadata {
  title: string;
  description: string;
}

export interface ImageData {
  path: string;
  title: string;
  description: string;
}

export interface UploadImageRequest {
  image: File;
  title: string;
  description: string;
}

export interface UpdateMetadataRequest {
  image_path: string;
  title: string;
  description: string;
}

export interface DeleteImageRequest {
  image_path: string;
}
