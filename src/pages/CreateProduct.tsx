import { Navigation } from "@/components/Navigation";
import ProductForm from "@/components/ProductForm";
import { useProductDetails } from "@/hooks/useProductDetails";
import { useNavigate } from "react-router-dom";

import { useState } from "react";
const CreateProduct = () => {
  const { createProduct, isCreating } = useProductDetails();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (data: any) => {
    setError(null);
    createProduct(data, {
      onSuccess: () => {
        navigate('/products');
      },
      onError: (err: any) => {
        setError(err?.message || 'Failed to create product. Please try again.');
      }
    });
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
            <span className="font-semibold">Error:</span> {error}
          </div>
        )}
        <ProductForm
          mode="create"
          onSubmit={handleSubmit}
          loading={isCreating}
        />
      </div>
    </div>
  );
};

export default CreateProduct;
