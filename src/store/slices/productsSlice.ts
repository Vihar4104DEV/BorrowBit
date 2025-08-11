import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { apiService, Product, ProductsResponse } from '../../services/api';

export interface ProductsState {
  products: Product[];
  loading: boolean;
  error: string | null;
  pagination: {
    count: number;
    next: string | null;
    previous: string | null;
    currentPage: number;
    pageSize: number;
  };
}

export interface FetchProductsParams {
  page?: number;
  pageSize?: number;
}

// Async thunk for fetching products
export const fetchProducts = createAsyncThunk(
  'products/fetchProducts',
  async (params: FetchProductsParams = {}, { rejectWithValue }) => {
    try {
      const { page = 1, pageSize = 10 } = params;
      const data = await apiService.getProducts(page, pageSize);
      return { data: data.data, page, pageSize };
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to fetch products');
    }
  }
);

const initialState: ProductsState = {
  products: [],
  loading: false,
  error: null,
  pagination: {
    count: 0,
    next: null,
    previous: null,
    currentPage: 1,
    pageSize: 10,
  },
};

const productsSlice = createSlice({
  name: 'products',
  initialState,
  reducers: {
    clearProducts: (state) => {
      state.products = [];
      state.error = null;
      state.pagination = {
        count: 0,
        next: null,
        previous: null,
        currentPage: 1,
        pageSize: 10,
      };
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchProducts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProducts.fulfilled, (state, action) => {
        state.loading = false;
        state.products = action.payload.data.results;
        state.pagination = {
          count: action.payload.data.count,
          next: action.payload.data.next,
          previous: action.payload.data.previous,
          currentPage: action.payload.page,
          pageSize: action.payload.pageSize,
        };
        state.error = null;
      })
      .addCase(fetchProducts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearProducts, clearError } = productsSlice.actions;
export default productsSlice.reducer;
