import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Switch } from './ui/switch';
import { Separator } from './ui/separator';
import { DatePicker } from './ui/date-picker';
import ImageUpload from './ui/image-upload';
import { useCategories } from '@/hooks/useCategories';
import { 
  Package, 
  Plus, 
  X, 
  Save, 
  ArrowLeft,
  Loader2,
  AlertCircle,
  CheckCircle,
  Sparkles,
  Star,
  Award,
  Zap,
  Settings
} from 'lucide-react';
import { toast } from 'sonner';

interface ProductFormProps {
  mode: 'create' | 'edit';
  initialData?: any;
  onSubmit: (data: any) => void;
  loading?: boolean;
}

const ProductForm: React.FC<ProductFormProps> = ({
  mode,
  initialData,
  onSubmit,
  loading = false
}) => {
  const navigate = useNavigate();
  const { categories, isLoading: categoriesLoading } = useCategories();
  const [formData, setFormData] = useState({
    name: '',
    category: '',
    short_description: '',
    description: '',
    specifications: {
      weight: '',
      dimensions: '',
      color: '',
      material: '',
      brand: '',
      model: ''
    },
    features: [''],
    dimensions: {
      length: 0,
      width: 0,
      height: 0
    },
    weight: '',
    color: '',
    material: '',
    brand: '',
    model: '',
    condition: 'GOOD',
    total_quantity: 1,
    deposit_amount: '',
    warehouse_location: '',
    storage_requirements: '',
    is_rentable: true,
    minimum_rental_duration: 1,
    maximum_rental_duration: 168,
    main_image: '',
    images: [''],
    meta_title: '',
    meta_description: '',
    keywords: '',
    is_featured: false,
    is_popular: false,
    admin_approved: false,
    sort_order: 0,
    purchase_date: undefined as Date | undefined,
    warranty_expiry: undefined as Date | undefined
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    if (initialData && mode === 'edit') {
      setFormData({
        ...formData,
        ...initialData,
        features: initialData.features || [''],
        images: initialData.images || [''],
        purchase_date: initialData.purchase_date ? new Date(initialData.purchase_date) : undefined,
        warranty_expiry: initialData.warranty_expiry ? new Date(initialData.warranty_expiry) : undefined
      });
    }
  }, [initialData, mode]);

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleSpecificationChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      specifications: { ...prev.specifications, [field]: value }
    }));
  };

  const handleDimensionChange = (field: string, value: number) => {
    setFormData(prev => ({
      ...prev,
      dimensions: { ...prev.dimensions, [field]: value }
    }));
  };

  const handleFeatureChange = (index: number, value: string) => {
    const newFeatures = [...formData.features];
    newFeatures[index] = value;
    setFormData(prev => ({ ...prev, features: newFeatures }));
  };

  const addFeature = () => {
    setFormData(prev => ({ ...prev, features: [...prev.features, ''] }));
  };

  const removeFeature = (index: number) => {
    const newFeatures = formData.features.filter((_, i) => i !== index);
    setFormData(prev => ({ ...prev, features: newFeatures }));
  };

  const handleImageChange = (index: number, value: string) => {
    const newImages = [...formData.images];
    newImages[index] = value;
    setFormData(prev => ({ ...prev, images: newImages }));
  };

  const addImage = () => {
    setFormData(prev => ({ ...prev, images: [...prev.images, ''] }));
  };

  const removeImage = (index: number) => {
    const newImages = formData.images.filter((_, i) => i !== index);
    setFormData(prev => ({ ...prev, images: newImages }));
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Product name is required';
    }

    if (!formData.category.trim()) {
      newErrors.category = 'Category is required';
    }

    if (!formData.short_description.trim()) {
      newErrors.short_description = 'Short description is required';
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    }

    if (!formData.deposit_amount || parseFloat(formData.deposit_amount) <= 0) {
      newErrors.deposit_amount = 'Valid deposit amount is required';
    }

    if (!formData.total_quantity || formData.total_quantity <= 0) {
      newErrors.total_quantity = 'Valid total quantity is required';
    }

    if (!formData.warehouse_location.trim()) {
      newErrors.warehouse_location = 'Warehouse location is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError(null);
    if (!validateForm()) {
      toast.error('Please fix the errors in the form');
      return;
    }

    // Clean up empty features and images
    const cleanedData = {
      ...formData,
      features: formData.features.filter(f => f.trim() !== ''),
      images: formData.images.filter(i => i.trim() !== '')
    };

    // Wrap onSubmit to catch errors
    try {
      onSubmit(cleanedData);
    } catch (err: any) {
      setSubmitError(err?.message || 'Failed to create product. Please try again.');
      toast.error(err?.message || 'Failed to create product.');
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {submitError && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
          <span className="font-semibold">Error:</span> {submitError}
        </div>
      )}
      <div className="flex flex-col lg:flex-row items-start lg:items-center gap-4 mb-8">
        <Button variant="outline" onClick={() => navigate(-1)} className="shrink-0">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <div className="flex-1 min-w-0">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 mb-2">
            <div className="p-2 bg-gradient-to-r from-primary to-primary/80 rounded-lg shrink-0">
              <Package className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-primary to-primary/80 bg-clip-text text-transparent">
              {mode === 'create' ? 'Create New Product' : 'Edit Product'}
            </h1>
          </div>
          <p className="text-muted-foreground text-base sm:text-lg">
            {mode === 'create' ? 'Add a new product to your inventory with detailed specifications' : 'Update and manage your product information'}
          </p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <div className="p-2 bg-green-100 rounded-lg">
            <Sparkles className="w-5 h-5 text-green-600" />
          </div>
          <span className="text-sm text-green-600 font-medium hidden sm:inline">Smart Form</span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Information */}
        <Card className="border-2 border-primary/10 shadow-lg">
          <CardHeader className="bg-gradient-to-r from-primary/5 to-primary/10 border-b">
            <CardTitle className="flex items-center gap-3 text-primary">
              <div className="p-2 bg-primary rounded-lg">
                <Package className="w-5 h-5 text-white" />
              </div>
              Basic Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">Product Name *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  placeholder="Enter product name"
                  className={errors.name ? 'border-red-500' : ''}
                />
                {errors.name && <p className="text-sm text-red-500">{errors.name}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="category">Category *</Label>
                <Select 
                  value={formData.category} 
                  onValueChange={(value) => handleInputChange('category', value)}
                >
                  <SelectTrigger className={errors.category ? 'border-red-500' : ''}>
                    <SelectValue placeholder="Select a category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categoriesLoading ? (
                      <SelectItem value={undefined} disabled>
                        Loading categories...
                      </SelectItem>
                    ) : (
                      (categories as any[]).map((category) => (
                        <SelectItem key={category.id} value={category.id}>
                          {category.name}
                        </SelectItem>
                      ))
                    )}
                  </SelectContent>
                </Select>
                {errors.category && <p className="text-sm text-red-500">{errors.category}</p>}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="short_description">Short Description *</Label>
              <Input
                id="short_description"
                value={formData.short_description}
                onChange={(e) => handleInputChange('short_description', e.target.value)}
                placeholder="Brief description of the product"
                className={errors.short_description ? 'border-red-500' : ''}
              />
              {errors.short_description && <p className="text-sm text-red-500">{errors.short_description}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Full Description *</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Detailed description of the product"
                rows={4}
                className={errors.description ? 'border-red-500' : ''}
              />
              {errors.description && <p className="text-sm text-red-500">{errors.description}</p>}
            </div>
          </CardContent>
        </Card>

        {/* Specifications */}
        <Card className="border-2 border-blue-100 shadow-lg">
          <CardHeader className="bg-gradient-to-r from-blue-50 to-blue-100 border-b">
            <CardTitle className="flex items-center gap-3 text-blue-700">
              <div className="p-2 bg-blue-600 rounded-lg">
                <Settings className="w-5 h-5 text-white" />
              </div>
              Specifications
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="weight">Weight</Label>
                <Input
                  id="weight"
                  value={formData.specifications.weight}
                  onChange={(e) => handleSpecificationChange('weight', e.target.value)}
                  placeholder="e.g., 2.5 kg"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="dimensions">Dimensions</Label>
                <Input
                  id="dimensions"
                  value={formData.specifications.dimensions}
                  onChange={(e) => handleSpecificationChange('dimensions', e.target.value)}
                  placeholder="e.g., 100 x 50 x 25 cm"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="color">Color</Label>
                <Input
                  id="color"
                  value={formData.specifications.color}
                  onChange={(e) => handleSpecificationChange('color', e.target.value)}
                  placeholder="e.g., Red"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="material">Material</Label>
                <Input
                  id="material"
                  value={formData.specifications.material}
                  onChange={(e) => handleSpecificationChange('material', e.target.value)}
                  placeholder="e.g., Plastic"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="brand">Brand</Label>
                <Input
                  id="brand"
                  value={formData.specifications.brand}
                  onChange={(e) => handleSpecificationChange('brand', e.target.value)}
                  placeholder="e.g., Generic Brand"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="model">Model</Label>
                <Input
                  id="model"
                  value={formData.specifications.model}
                  onChange={(e) => handleSpecificationChange('model', e.target.value)}
                  placeholder="e.g., Model-123"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Features */}
        <Card>
          <CardHeader>
            <CardTitle>Features</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {formData.features.map((feature, index) => (
              <div key={index} className="flex gap-2">
                <Input
                  value={feature}
                  onChange={(e) => handleFeatureChange(index, e.target.value)}
                  placeholder="Enter feature"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={() => removeFeature(index)}
                  disabled={formData.features.length === 1}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            ))}
            <Button type="button" variant="outline" onClick={addFeature}>
              <Plus className="w-4 h-4 mr-2" />
              Add Feature
            </Button>
          </CardContent>
        </Card>

        {/* Dimensions */}
        <Card>
          <CardHeader>
            <CardTitle>Dimensions (cm)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="length">Length</Label>
                <Input
                  id="length"
                  type="number"
                  value={formData.dimensions.length}
                  onChange={(e) => handleDimensionChange('length', parseFloat(e.target.value) || 0)}
                  placeholder="0"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="width">Width</Label>
                <Input
                  id="width"
                  type="number"
                  value={formData.dimensions.width}
                  onChange={(e) => handleDimensionChange('width', parseFloat(e.target.value) || 0)}
                  placeholder="0"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="height">Height</Label>
                <Input
                  id="height"
                  type="number"
                  value={formData.dimensions.height}
                  onChange={(e) => handleDimensionChange('height', parseFloat(e.target.value) || 0)}
                  placeholder="0"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Product Details */}
        <Card>
          <CardHeader>
            <CardTitle>Product Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="condition">Condition</Label>
                <Select value={formData.condition} onValueChange={(value) => handleInputChange('condition', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select condition" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="EXCELLENT">Excellent</SelectItem>
                    <SelectItem value="GOOD">Good</SelectItem>
                    <SelectItem value="FAIR">Fair</SelectItem>
                    <SelectItem value="POOR">Poor</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="total_quantity">Total Quantity *</Label>
                <Input
                  id="total_quantity"
                  type="number"
                  value={formData.total_quantity}
                  onChange={(e) => handleInputChange('total_quantity', parseInt(e.target.value) || 0)}
                  placeholder="1"
                  className={errors.total_quantity ? 'border-red-500' : ''}
                />
                {errors.total_quantity && <p className="text-sm text-red-500">{errors.total_quantity}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="deposit_amount">Deposit Amount ($) *</Label>
                <Input
                  id="deposit_amount"
                  type="number"
                  step="0.01"
                  value={formData.deposit_amount}
                  onChange={(e) => handleInputChange('deposit_amount', e.target.value)}
                  placeholder="0.00"
                  className={errors.deposit_amount ? 'border-red-500' : ''}
                />
                {errors.deposit_amount && <p className="text-sm text-red-500">{errors.deposit_amount}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="warehouse_location">Warehouse Location *</Label>
                <Input
                  id="warehouse_location"
                  value={formData.warehouse_location}
                  onChange={(e) => handleInputChange('warehouse_location', e.target.value)}
                  placeholder="e.g., Section A-1"
                  className={errors.warehouse_location ? 'border-red-500' : ''}
                />
                {errors.warehouse_location && <p className="text-sm text-red-500">{errors.warehouse_location}</p>}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="storage_requirements">Storage Requirements</Label>
              <Textarea
                id="storage_requirements"
                value={formData.storage_requirements}
                onChange={(e) => handleInputChange('storage_requirements', e.target.value)}
                placeholder="Describe storage requirements"
                rows={3}
              />
            </div>
          </CardContent>
        </Card>

        {/* Rental Settings */}
        <Card>
          <CardHeader>
            <CardTitle>Rental Settings</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center space-x-2">
              <Switch
                id="is_rentable"
                checked={formData.is_rentable}
                onCheckedChange={(checked) => handleInputChange('is_rentable', checked)}
              />
              <Label htmlFor="is_rentable">Available for Rent</Label>
            </div>

            {formData.is_rentable && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="minimum_rental_duration">Minimum Rental Duration (hours)</Label>
                  <Input
                    id="minimum_rental_duration"
                    type="number"
                    value={formData.minimum_rental_duration}
                    onChange={(e) => handleInputChange('minimum_rental_duration', parseInt(e.target.value) || 1)}
                    placeholder="1"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="maximum_rental_duration">Maximum Rental Duration (hours)</Label>
                  <Input
                    id="maximum_rental_duration"
                    type="number"
                    value={formData.maximum_rental_duration}
                    onChange={(e) => handleInputChange('maximum_rental_duration', parseInt(e.target.value) || 168)}
                    placeholder="168"
                  />
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Images */}
        <Card>
          <CardHeader>
            <CardTitle>Images</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <ImageUpload
              value={formData.main_image}
              onChange={(value) => handleInputChange('main_image', value)}
              label="Main Image"
              placeholder="Upload main product image"
            />

            <div className="space-y-2">
              <Label>Additional Images</Label>
              {formData.images.map((image, index) => (
                <div key={index} className="flex gap-2">
                  <Input
                    value={image}
                    onChange={(e) => handleImageChange(index, e.target.value)}
                    placeholder="https://example.com/image.jpg"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    onClick={() => removeImage(index)}
                    disabled={formData.images.length === 1}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              ))}
              <Button type="button" variant="outline" onClick={addImage}>
                <Plus className="w-4 h-4 mr-2" />
                Add Image
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* SEO & Meta */}
        <Card>
          <CardHeader>
            <CardTitle>SEO & Meta Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="meta_title">Meta Title</Label>
              <Input
                id="meta_title"
                value={formData.meta_title}
                onChange={(e) => handleInputChange('meta_title', e.target.value)}
                placeholder="SEO title for the product"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="meta_description">Meta Description</Label>
              <Textarea
                id="meta_description"
                value={formData.meta_description}
                onChange={(e) => handleInputChange('meta_description', e.target.value)}
                placeholder="SEO description for the product"
                rows={3}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="keywords">Keywords</Label>
              <Input
                id="keywords"
                value={formData.keywords}
                onChange={(e) => handleInputChange('keywords', e.target.value)}
                placeholder="keyword1, keyword2, keyword3"
              />
            </div>
          </CardContent>
        </Card>

        {/* Product Flags */}
        <Card>
          <CardHeader>
            <CardTitle>Product Flags</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center space-x-2">
              <Switch
                id="is_featured"
                checked={formData.is_featured}
                onCheckedChange={(checked) => handleInputChange('is_featured', checked)}
              />
              <Label htmlFor="is_featured">Featured Product</Label>
            </div>

            <div className="flex items-center space-x-2">
              <Switch
                id="is_popular"
                checked={formData.is_popular}
                onCheckedChange={(checked) => handleInputChange('is_popular', checked)}
              />
              <Label htmlFor="is_popular">Popular Product</Label>
            </div>

            <div className="flex items-center space-x-2">
              <Switch
                id="admin_approved"
                checked={formData.admin_approved}
                onCheckedChange={(checked) => handleInputChange('admin_approved', checked)}
              />
              <Label htmlFor="admin_approved">Admin Approved</Label>
            </div>

            <div className="space-y-2">
              <Label htmlFor="sort_order">Sort Order</Label>
              <Input
                id="sort_order"
                type="number"
                value={formData.sort_order}
                onChange={(e) => handleInputChange('sort_order', parseInt(e.target.value) || 0)}
                placeholder="0"
              />
            </div>
          </CardContent>
        </Card>

        {/* Dates */}
        <Card>
          <CardHeader>
            <CardTitle>Important Dates</CardTitle>
          </CardHeader>
          <CardContent>
                         <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
               <div className="space-y-2">
                 <Label htmlFor="purchase_date">Purchase Date</Label>
                 <DatePicker
                   date={formData.purchase_date}
                   onDateChange={(date) => handleInputChange('purchase_date', date)}
                   placeholder="Select purchase date"
                 />
               </div>

               <div className="space-y-2">
                 <Label htmlFor="warranty_expiry">Warranty Expiry</Label>
                 <DatePicker
                   date={formData.warranty_expiry}
                   onDateChange={(date) => handleInputChange('warranty_expiry', date)}
                   placeholder="Select warranty expiry date"
                 />
               </div>
             </div>
          </CardContent>
        </Card>

        {/* Submit Button */}
        <Card className="border-2 border-green-100 bg-gradient-to-r from-green-50 to-green-100">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-600 rounded-lg">
                  <Save className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-green-800">Ready to {mode === 'create' ? 'Create' : 'Update'}?</h3>
                  <p className="text-sm text-green-600">Review your information and submit the form</p>
                </div>
              </div>
              <div className="flex gap-4">
                <Button type="button" variant="outline" onClick={() => navigate(-1)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={loading} className="bg-green-600 hover:bg-green-700">
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      {mode === 'create' ? 'Creating...' : 'Updating...'}
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4 mr-2" />
                      {mode === 'create' ? 'Create Product' : 'Update Product'}
                    </>
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  );
};

export default ProductForm;
