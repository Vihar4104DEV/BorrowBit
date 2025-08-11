import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { fetchProductDetails, createProduct, updateProduct, clearProductDetails } from '../store/slices/productDetailsSlice';
import { toast } from 'sonner';

export const useProductDetails = () => {
  const dispatch = useAppDispatch();
  const queryClient = useQueryClient();
  
  const { product, loading, error } = useAppSelector((state) => state.productDetails);

  const fetchProductDetailsMutation = useMutation({
    mutationFn: async (productId: string) => {
      const result = await dispatch(fetchProductDetails(productId)).unwrap();
      return result;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['productDetails'] });
    },
    onError: (error: string) => {
      toast.error(error || 'Failed to fetch product details');
    },
  });

  const createProductMutation = useMutation({
    mutationFn: async (productData: any) => {
      const result = await dispatch(createProduct(productData)).unwrap();
      return result;
    },
    onSuccess: (data) => {
      toast.success('Product created successfully!');
      queryClient.invalidateQueries({ queryKey: ['products'] });
      queryClient.invalidateQueries({ queryKey: ['productDetails'] });
    },
    onError: (error: string) => {
      toast.error(error || 'Failed to create product');
    },
  });

  const updateProductMutation = useMutation({
    mutationFn: async ({ id, productData }: { id: string; productData: any }) => {
      const result = await dispatch(updateProduct({ id, productData })).unwrap();
      return result;
    },
    onSuccess: (data) => {
      toast.success('Product updated successfully!');
      queryClient.invalidateQueries({ queryKey: ['products'] });
      queryClient.invalidateQueries({ queryKey: ['productDetails'] });
    },
    onError: (error: string) => {
      toast.error(error || 'Failed to update product');
    },
  });

  const clearProductData = () => {
    dispatch(clearProductDetails());
    queryClient.removeQueries({ queryKey: ['productDetails'] });
  };

  return {
    product,
    loading,
    error,
    fetchProductDetails: fetchProductDetailsMutation.mutate,
    createProduct: createProductMutation.mutate,
    updateProduct: updateProductMutation.mutate,
    clearProductDetails: clearProductData,
    isFetching: fetchProductDetailsMutation.isPending,
    isCreating: createProductMutation.isPending,
    isUpdating: updateProductMutation.isPending,
  };
};
