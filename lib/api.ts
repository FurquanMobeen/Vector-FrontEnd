import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  LoginRequest,
  LoginResponse,
  SearchResult,
  ImageData,
  UploadImageRequest,
  UpdateMetadataRequest,
  ApiError,
} from './types';

const AUTH_API_URL = process.env.NEXT_PUBLIC_AUTH_API_URL || 'http://localhost:8000';
const VECTOR_SEARCH_API_URL = process.env.NEXT_PUBLIC_VECTOR_SEARCH_API_URL || 'http://localhost:8001';

class ApiClient {
  private authClient: AxiosInstance;
  private vectorClient: AxiosInstance;

  constructor() {
    // Auth API client
    this.authClient = axios.create({
      baseURL: AUTH_API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Vector Search API client
    this.vectorClient = axios.create({
      baseURL: VECTOR_SEARCH_API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add interceptors to both clients
    const addInterceptors = (client: AxiosInstance) => {
      // Request interceptor to add auth token
      client.interceptors.request.use(
        (config) => {
          if (typeof window !== 'undefined') {
            const token = localStorage.getItem('access_token');
            if (token) {
              config.headers.Authorization = `Bearer ${token}`;
            }
          }
          return config;
        },
        (error) => Promise.reject(error)
      );

      // Response interceptor for error handling
      client.interceptors.response.use(
        (response) => response,
        (error: AxiosError<ApiError>) => {
          if (error.response?.status === 401) {
            // Unauthorized - clear token and redirect to login
            if (typeof window !== 'undefined') {
              localStorage.removeItem('access_token');
              localStorage.removeItem('user');
              window.location.href = '/login';
            }
          }
          return Promise.reject(error);
        }
      );
    };

    addInterceptors(this.authClient);
    addInterceptors(this.vectorClient);
  }

  // Authentication
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await this.authClient.post<LoginResponse>('/api/auth/login', credentials);
    return response.data;
  }

  async getCurrentUser(): Promise<any> {
    const response = await this.authClient.get('/api/auth/me');
    return response.data;
  }

  // Vector Search - Image Search
  async searchByImage(image: File, k: number = 9): Promise<SearchResult[]> {
    const formData = new FormData();
    formData.append('image', image);

    const response = await this.vectorClient.post<{results: SearchResult[], total: number}>(`/api/search/image?k=${k}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data.results;
  }

  // Vector Search - Text Search
  async searchByText(query: string, k: number = 9): Promise<SearchResult[]> {
    const response = await this.vectorClient.post<{results: SearchResult[], total: number}>('/api/search/text', {
      query,
      k,
    });
    return response.data.results;
  }

  // Image Management - Get all images
  async getAllImages(): Promise<ImageData[]> {
    const response = await this.vectorClient.get<ImageData[]>('/api/images');
    return response.data;
  }

  // Image Management - Upload new image
  async uploadImage(data: UploadImageRequest): Promise<{ message: string }> {
    const formData = new FormData();
    formData.append('image', data.image);
    formData.append('title', data.title);
    formData.append('description', data.description);

    const response = await this.vectorClient.post<{ message: string }>('/api/images', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Image Management - Update image metadata
  async updateMetadata(data: UpdateMetadataRequest): Promise<{ message: string }> {
    const response = await this.vectorClient.put<{ message: string }>(
      `/api/images/${encodeURIComponent(data.image_path)}/metadata`,
      {
        title: data.title,
        description: data.description,
      }
    );
    return response.data;
  }

  // Image Management - Delete image
  async deleteImage(imagePath: string): Promise<{ message: string }> {
    const response = await this.vectorClient.delete<{ message: string }>(
      `/api/images/${encodeURIComponent(imagePath)}`
    );
    return response.data;
  }

  // Image Management - Export metadata
  async exportMetadata(imagePath?: string): Promise<any> {
    const params = imagePath ? { image_path: imagePath } : {};
    const response = await this.vectorClient.get('/api/images/metadata/export', { params });
    return response.data;
  }
}

export const apiClient = new ApiClient();
