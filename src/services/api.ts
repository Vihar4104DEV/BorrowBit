const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://easily-bold-elephant.ngrok-free.app/api/v1';

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface ApiError {
  message: string;
  status?: number;
}

export interface User {
  id: string;
  email: string;
  phone_number: string;
  first_name: string;
  last_name: string;
  prefix: string;
  is_verified: boolean;
  email_verified_at: string | null;
  phone_verified_at: string | null;
  user_role?: string;
}

export interface AuthData {
  user: User;
  refresh: string;
  access: string;
}

export interface OtpData {
  user: User;
}

export interface BasicPricing {
  daily_rate: string;
  hourly_rate: string | null;
  weekly_rate: string | null;
  monthly_rate: string | null;
  setup_fee: string;
  delivery_fee: string;
  currency: string;
}

export interface Product {
  id: string;
  name: string;
  slug: string;
  sku: string;
  category: string;
  category_name: string;
  owner: string;
  owner_name: string;
  short_description: string;
  condition: string;
  status: string;
  available_quantity: number;
  deposit_amount: string;
  main_image_url: string | null;
  average_rating: number;
  review_count: number;
  basic_pricing: BasicPricing;
  is_featured: boolean;
  is_popular: boolean;
  admin_approved: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Product[];
}

// Product Details Types
export interface Category {
  id: string;
  name: string;
  slug: string;
  description: string;
  parent: string | null;
  image: string | null;
  icon: string;
  sort_order: number;
  is_featured: boolean;
  products_count: number;
  children: Category[];
  created_at: string;
  updated_at: string;
}

export interface Specifications {
  weight: string;
  dimensions: string;
  color: string;
  material: string;
  brand: string;
  model: string;
}

export interface Dimensions {
  length: number;
  width: number;
  height: number;
}

export interface PricingRule {
  id: string;
  customer_type: string;
  duration_type: string;
  base_price: string;
  price_per_unit: string;
  hourly_rate: string | null;
  daily_rate: string | null;
  weekly_rate: string | null;
  monthly_rate: string | null;
  discount_percentage: string;
  bulk_discount_threshold: number;
  bulk_discount_percentage: string;
  seasonal_multiplier: string;
  valid_from: string | null;
  valid_to: string | null;
  setup_fee: string;
  delivery_fee: string;
  late_return_fee_per_day: string;
  priority: number;
  overrides_lower_priority: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductDetails {
  id: string;
  name: string;
  slug: string;
  sku: string;
  owner: string;
  owner_name: string;
  category: Category;
  short_description: string;
  description: string;
  specifications: Specifications;
  features: string[];
  dimensions: Dimensions;
  weight: string;
  color: string;
  material: string;
  brand: string;
  model: string;
  condition: string;
  status: string;
  total_quantity: number;
  available_quantity: number;
  reserved_quantity: number;
  minimum_quantity: number;
  deposit_amount: string;
  warehouse_location: string;
  storage_requirements: string;
  is_rentable: boolean;
  minimum_rental_duration: number;
  maximum_rental_duration: number;
  main_image: string | null;
  images: string[];
  meta_title: string;
  meta_description: string;
  keywords: string;
  is_featured: boolean;
  is_popular: boolean;
  admin_approved: boolean;
  sort_order: number;
  purchase_date: string;
  warranty_expiry: string;
  last_maintenance: string;
  next_maintenance: string;
  pricing_rules: PricingRule[];
}

export interface Category {
  id: string;
  name: string;
  slug: string;
}

export interface CategoriesResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Category[];
}

export interface CreateProductRequest {
  name: string;
  category: string;
  short_description: string;
  description: string;
  specifications: Specifications;
  features: string[];
  dimensions: Dimensions;
  weight: string;
  color: string;
  material: string;
  brand: string;
  model: string;
  condition: string;
  total_quantity: number;
  deposit_amount: string;
  warehouse_location: string;
  storage_requirements: string;
  is_rentable: boolean;
  minimum_rental_duration: number;
  maximum_rental_duration: number;
  main_image?: any;
  images?: string[];
  meta_title?: string;
  meta_description?: string;
  keywords?: string;
  is_featured?: boolean;
  is_popular?: boolean;
  admin_approved?: boolean;
  sort_order?: number;
  purchase_date?: string;
  warranty_expiry?: string;
}

class ApiService {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    
    // Base headers that should always be included
    const defaultHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'ngrok-skip-browser-warning': 'true',
    };

    // Add authorization header if token exists
    const token = localStorage.getItem('accessToken');
    if (token) {
      defaultHeaders['Authorization'] = `Bearer ${token}`;
    }

    // Merge headers properly, ensuring ngrok header is always present
    const finalHeaders = {
      ...defaultHeaders,
      ...options.headers,
    };

    const config: RequestInit = {
      ...options,
      headers: finalHeaders,
      // Ensure CORS mode is set properly
      mode: 'cors',
      credentials: 'include', // Include credentials if needed
    };

    try {
      console.log('Making API request to:', url);
      console.log('Request config:', config);
      
      const response = await fetch(url, config);
      
      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);
      
      // Handle 401 Unauthorized - redirect to login
      if (response.status === 401) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('userId');
        window.location.href = '/login';
        throw new Error('Unauthorized - Please login again');
      }
      
      // Check if response is ok before trying to parse JSON
      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        
        try {
          const errorData = await response.json();
          errorMessage = errorData.message || errorMessage;
        } catch (parseError) {
          // If we can't parse the error response, use the status text
          errorMessage = response.statusText || errorMessage;
        }
        
        throw new Error(errorMessage);
      }

      const data = await response.json();
      console.log('Response data:', data);
      
      return data;
    } catch (error) {
      console.error('API request failed:', error);
      
      if (error instanceof Error) {
        // Check if it's a CORS error
        if (error.message.includes('CORS') || error.message.includes('Failed to fetch')) {
          throw new Error('CORS error: Unable to connect to the server. Please check your network connection.');
        }
        throw new Error(error.message);
      }
      
      throw new Error('An unexpected error occurred');
    }
  }

  // Auth endpoints with proper return types
  async signup(credentials: {
    first_name: string;
    last_name: string;
    prefix: string;
    phone_number: string;
    email: string;
    password: string;
  }): Promise<ApiResponse<AuthData>> {
    return this.request<AuthData>('/user/register/', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async login(credentials: { email: string; password: string }): Promise<ApiResponse<AuthData>> {
    return this.request<AuthData>('/user/login/', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async verifyOtp(otpData: {
    otp: string;
    otp_type: 'email' | 'phone';
    phone_number?: string;
    email?: string;
  }): Promise<ApiResponse<OtpData>> {
    return this.request<OtpData>('/user/verify-otp/', {
      method: 'POST',
      body: JSON.stringify(otpData),
    });
  }

  // Profile endpoint
  async getProfile(): Promise<ApiResponse<AuthData>> {
    return this.request<AuthData>('/user/profile/', {
      method: 'GET',
    });
  }

  // Products endpoints
  async getProducts(page: number = 1, pageSize: number = 5): Promise<ApiResponse<ProductsResponse>> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });
    
    return this.request<ProductsResponse>(`/products/products/?${params}`, {
      method: 'GET',
    });
  }

  async getCategories(): Promise<ApiResponse<CategoriesResponse>> {
    return this.request<CategoriesResponse>('/products/categories/', {
      method: 'GET',
    });
  }

  async getProductDetails(id: string): Promise<ApiResponse<ProductDetails>> {
    return this.request<ProductDetails>(`/products/products/${id}/`, {
      method: 'GET',
    });
  }

  async createProduct(productData: CreateProductRequest): Promise<ApiResponse<ProductDetails>> {
    return this.request<ProductDetails>('/products/products/', {
      method: 'POST',
      body: JSON.stringify(productData),
    });
  }

  async updateProduct(id: string, productData: Partial<CreateProductRequest>): Promise<ApiResponse<ProductDetails>> {
    return this.request<ProductDetails>(`/products/products/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(productData),
    });
  }

  // Generic GET request
  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  // Generic POST request
  async post<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Generic PUT request
  async put<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // Generic DELETE request
  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

export const apiService = new ApiService(API_BASE_URL);
export default apiService;
