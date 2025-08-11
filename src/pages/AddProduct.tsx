import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Navigation } from "@/components/Navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Package,
  ArrowLeft,
  Save,
  Upload,
  DollarSign,
  Hash,
  FileText,
  Image as ImageIcon,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const AddProduct = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  
  // Determine where to go back based on referrer
  const getBackPath = () => {
    const referrer = location.state?.from || document.referrer;
    if (referrer.includes('/my-products')) {
      return '/my-products';
    }
    return '/products';
  };
  
  const [formData, setFormData] = useState({
    name: "",
    category: "",
    status: "available",
    dailyRate: "",
    weeklyRate: "",
    monthlyRate: "",
    stock: "",
    totalRentals: "0",
    image: "/placeholder.svg",
    description: "",
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  const categories = [
    "Photography", "Event Equipment", "Audio", "Vehicles", 
    "Tools & Equipment", "Lighting", "Furniture", "Electronics", 
    "Sports Equipment", "Other"
  ];

  const statusOptions = [
    { value: "available", label: "Available", color: "bg-success text-success-foreground" },
    { value: "rented", label: "Rented", color: "bg-warning text-warning-foreground" },
    { value: "maintenance", label: "Maintenance", color: "bg-destructive text-destructive-foreground" },
  ];

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const calculateRates = () => {
    const daily = parseFloat(formData.dailyRate) || 0;
    if (daily > 0) {
      setFormData(prev => ({
        ...prev,
        weeklyRate: (daily * 6).toString(),
        monthlyRate: (daily * 30).toString()
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    const requiredFields = ['name', 'category', 'dailyRate', 'stock'];
    const missingFields = requiredFields.filter(field => !formData[field as keyof typeof formData]);
    
    if (missingFields.length > 0) {
      toast({
        title: "Validation Error",
        description: `Please fill in all required fields: ${missingFields.join(', ')}`,
        variant: "destructive",
      });
      setIsSubmitting(false);
      return;
    }

    setTimeout(() => {
      toast({
        title: "Product Added Successfully",
        description: `${formData.name} has been added to the catalog`,
      });
      setIsSubmitting(false);
      navigate('/products');
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                 <div className="mb-8">
           <Button
             variant="ghost"
             size="sm"
             onClick={() => navigate(getBackPath())}
             className="flex items-center gap-2 mb-4 text-muted-foreground hover:text-foreground"
           >
             <ArrowLeft className="w-4 h-4" />
             Back to Products
           </Button>
           <div>
             <h1 className="text-3xl font-bold text-foreground mb-2">Add New Product</h1>
             <p className="text-muted-foreground">Create a new product for your rental catalog</p>
           </div>
         </div>

        <form onSubmit={handleSubmit} className="max-w-2xl mx-auto">
          <div className="space-y-6">
            {/* Product Name */}
            <div className="space-y-2">
              <Label htmlFor="name">Product Name *</Label>
              <Input
                id="name"
                placeholder="Enter product name"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                required
              />
            </div>

            {/* Category */}
            <div className="space-y-2">
              <Label htmlFor="category">Category *</Label>
              <Select value={formData.category} onValueChange={(value) => handleInputChange('category', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((category) => (
                    <SelectItem key={category} value={category}>
                      {category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                placeholder="Describe the product features and specifications"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                rows={4}
              />
            </div>

            {/* Daily Rate */}
            <div className="space-y-2">
              <Label htmlFor="dailyRate">Daily Rate *</Label>
              <div className="relative">
                <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  id="dailyRate"
                  type="number"
                  placeholder="0.00"
                  value={formData.dailyRate}
                  onChange={(e) => handleInputChange('dailyRate', e.target.value)}
                  onBlur={calculateRates}
                  className="pl-10"
                  required
                />
              </div>
            </div>

            {/* Weekly Rate */}
            <div className="space-y-2">
              <Label htmlFor="weeklyRate">Weekly Rate</Label>
              <div className="relative">
                <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  id="weeklyRate"
                  type="number"
                  placeholder="0.00"
                  value={formData.weeklyRate}
                  onChange={(e) => handleInputChange('weeklyRate', e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Monthly Rate */}
            <div className="space-y-2">
              <Label htmlFor="monthlyRate">Monthly Rate</Label>
              <div className="relative">
                <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  id="monthlyRate"
                  type="number"
                  placeholder="0.00"
                  value={formData.monthlyRate}
                  onChange={(e) => handleInputChange('monthlyRate', e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Stock Quantity */}
            <div className="space-y-2">
              <Label htmlFor="stock">Stock Quantity *</Label>
              <Input
                id="stock"
                type="number"
                placeholder="0"
                value={formData.stock}
                onChange={(e) => handleInputChange('stock', e.target.value)}
                required
              />
            </div>

            {/* Total Rentals */}
            <div className="space-y-2">
              <Label htmlFor="totalRentals">Total Rentals</Label>
              <Input
                id="totalRentals"
                type="number"
                placeholder="0"
                value={formData.totalRentals}
                onChange={(e) => handleInputChange('totalRentals', e.target.value)}
              />
            </div>

            {/* Status */}
            <div className="space-y-2">
              <Label htmlFor="status">Status</Label>
              <Select value={formData.status} onValueChange={(value) => handleInputChange('status', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  {statusOptions.map((status) => (
                    <SelectItem key={status.value} value={status.value}>
                      <div className="flex items-center gap-2">
                        <Badge className={status.color}>
                          {status.label}
                        </Badge>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Product Image */}
            <div className="space-y-2">
              <Label>Product Image</Label>
              <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-6 text-center">
                <Upload className="w-8 h-8 mx-auto mb-2 text-muted-foreground" />
                <p className="text-sm text-muted-foreground mb-2">
                  Upload product image
                </p>
                <Button variant="outline" size="sm">
                  Choose File
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                Supported formats: JPG, PNG, WebP (Max 5MB)
              </p>
            </div>

            {/* Preview */}
            <div className="space-y-2">
              <Label>Preview</Label>
              <div className="bg-muted rounded-lg p-4">
                <h4 className="font-semibold mb-2">
                  {formData.name || "Product Name"}
                </h4>
                <p className="text-sm text-muted-foreground mb-2">
                  {formData.category || "Category"}
                </p>
                {formData.status && (
                  <Badge className={statusOptions.find(s => s.value === formData.status)?.color}>
                    {statusOptions.find(s => s.value === formData.status)?.label}
                  </Badge>
                )}
                {formData.dailyRate && (
                  <p className="text-sm mt-2">
                    Daily Rate: <span className="font-semibold">${formData.dailyRate}</span>
                  </p>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 pt-4">
              <Button
                type="submit"
                className="flex-1"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                    Adding Product...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    Add Product
                  </>
                )}
              </Button>
              <Button
                type="button"
                variant="outline"
                className="flex-1"
                onClick={() => navigate(getBackPath())}
              >
                Cancel
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddProduct;
