import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { apiService, ProductDetails } from '../../services/api';

export interface ProductDetailsState {
  product: ProductDetails | null;
  loading: boolean;
  error: string | null;
}

// Async thunk for fetching product details
export const fetchProductDetails = createAsyncThunk(
  'productDetails/fetchProductDetails',
  async (productId: string, { rejectWithValue }) => {
    try {
      const data = await apiService.getProductDetails(productId);
      return data.data;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to fetch product details');
    }
  }
);

// Async thunk for creating product
export const createProduct = createAsyncThunk(
  'productDetails/createProduct',
  async (productData: any, { rejectWithValue }) => {
    try {
      const data = await apiService.createProduct(productData);
      return data.data;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to create product');
    }
  }
);

// Async thunk for updating product
export const updateProduct = createAsyncThunk(
  'productDetails/updateProduct',
  async ({ id, productData }: { id: string; productData: any }, { rejectWithValue }) => {
    try {
      const data = await apiService.updateProduct(id, productData);
      return data.data;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to update product');
    }
  }
);

const initialState: ProductDetailsState = {
  product: null,
  loading: false,
  error: null,
};

const productDetailsSlice = createSlice({
  name: 'productDetails',
  initialState,
  reducers: {
    clearProductDetails: (state) => {
      state.product = null;
      state.error = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // Fetch Product Details
    builder
      .addCase(fetchProductDetails.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProductDetails.fulfilled, (state, action) => {
        state.loading = false;
        state.product = action.payload;
        state.error = null;
      })
      .addCase(fetchProductDetails.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Create Product
    builder
      .addCase(createProduct.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createProduct.fulfilled, (state, action) => {
        state.loading = false;
        state.product = action.payload;
        state.error = null;
      })
      .addCase(createProduct.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });

    // Update Product
    builder
      .addCase(updateProduct.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateProduct.fulfilled, (state, action) => {
        state.loading = false;
        state.product = action.payload;
        state.error = null;
      })
      .addCase(updateProduct.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearProductDetails, clearError } = productDetailsSlice.actions;
export default productDetailsSlice.reducer;
