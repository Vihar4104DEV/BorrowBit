import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { fetchProducts, clearProducts } from '../store/slices/productsSlice';
import { toast } from 'sonner';

export const useProducts = () => {
  const dispatch = useAppDispatch();
  const queryClient = useQueryClient();
  
  const { products, loading, error, pagination } = useAppSelector((state) => state.products);

  const fetchProductsMutation = useMutation({
    mutationFn: async (params: { page?: number; pageSize?: number } = {}) => {
      const result = await dispatch(fetchProducts(params)).unwrap();
      return result;
    },
    onSuccess: (data) => {
      // Invalidate and refetch products query
      queryClient.invalidateQueries({ queryKey: ['products'] });
    },
    onError: (error: string) => {
      toast.error(error || 'Failed to fetch products');
    },
  });

  const clearProductsData = () => {
    dispatch(clearProducts());
    queryClient.removeQueries({ queryKey: ['products'] });
  };

  return {
    products,
    loading,
    error,
    pagination,
    fetchProducts: fetchProductsMutation.mutate,
    clearProducts: clearProductsData,
    isFetching: fetchProductsMutation.isPending,
  };
};
