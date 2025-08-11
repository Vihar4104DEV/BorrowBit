import { useQuery } from '@tanstack/react-query';
import { apiService } from '../services/api';
import { toast } from 'sonner';

export const useCategories = () => {
  const {
    data: categories,
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      try {
        const response = await apiService.getCategories();
        return response.data.results;
      } catch (error) {
        toast.error('Failed to fetch categories');
        throw error;
      }
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  });

  return {
    categories: categories || [],
    isLoading,
    error,
    refetch
  };
};
