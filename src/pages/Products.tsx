import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Navigation } from "@/components/Navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Search,
  Filter,
  Calendar,
  DollarSign,
  Package,
  Clock,
  CheckCircle,
  AlertCircle,
  Eye,
  Edit,
  Star,
  ChevronLeft,
  ChevronRight,
  Loader2,
  X,
} from "lucide-react";
import { useProducts } from "@/hooks/useProducts";
import { useAuth } from "@/hooks/useAuth";
import { useCart } from "@/contexts/CartContext";
import { DateSelectionDialog } from "@/components/DateSelectionDialog";

const Products = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const navigate = useNavigate();
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const { products, loading, error, pagination, fetchProducts, isFetching } = useProducts();
  
  const { user, isAuthenticated } = useAuth();
  const { addToCart } = useCart();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<any>(null);

  // Fetch products on component mount and page change
  useEffect(() => {
    fetchProducts({ page: currentPage, pageSize: 6 });
  }, [currentPage, fetchProducts]);

  // Get unique product names for filtering
  const productNames = Array.from(new Set(products.map(product => product.name))).sort();

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case "available":
        return (
          <Badge className="bg-success text-success-foreground">
            <CheckCircle className="w-3 h-3 mr-1" />Available
          </Badge>
        );
      case "rented":
        return (
          <Badge className="bg-warning text-warning-foreground">
            <Clock className="w-3 h-3 mr-1" />Rented
          </Badge>
        );
      case "maintenance":
        return (
          <Badge variant="destructive">
            <AlertCircle className="w-3 h-3 mr-1" />Maintenance
          </Badge>
        );
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const getConditionBadge = (condition: string) => {
    switch (condition.toLowerCase()) {
      case "excellent":
        return <Badge className="bg-green-100 text-green-800">Excellent</Badge>;
      case "good":
        return <Badge className="bg-blue-100 text-blue-800">Good</Badge>;
      case "fair":
        return <Badge className="bg-yellow-100 text-yellow-800">Fair</Badge>;
      default:
        return <Badge variant="secondary">{condition}</Badge>;
    }
  };

  // Filter by product name (dropdown) and search term
  const filteredProducts = products.filter((product) => {
    const matchesName = selectedCategory ? product.name === selectedCategory : true;
    const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      product.category_name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesName && matchesSearch;
  });

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const totalPages = Math.ceil(pagination.count / pagination.pageSize);

  // Loading skeleton for products
  const ProductSkeleton = () => (
    <Card className="shadow-card">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <Skeleton className="h-6 w-3/4 mb-2" />
            <Skeleton className="h-4 w-1/2 mb-2" />
            <Skeleton className="h-5 w-20" />
          </div>
          <Skeleton className="w-20 h-20 rounded-lg" />
        </div>
      </CardHeader>
      <CardContent>
        <Skeleton className="h-4 w-full mb-4" />
        <Skeleton className="h-4 w-3/4 mb-4" />
        <div className="space-y-2 mb-4">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
        </div>
        <div className="flex gap-2">
          <Skeleton className="h-8 flex-1" />
          <Skeleton className="h-8 flex-1" />
          <Skeleton className="h-8 flex-1" />
        </div>
      </CardContent>
    </Card>
  );

  return (
    <>
      <div className="min-h-screen bg-background">
        <Navigation />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-foreground mb-2">Product Catalog</h1>
              <p className="text-muted-foreground">Browse and manage rental products</p>
            </div>
            <Button variant="hero" size="lg" className="mt-4 sm:mt-0" onClick={() => navigate('/products/create')}>
              <Package className="w-4 h-4 mr-2" />
              Add New Product
            </Button>
          </div>

          {/* Search and Filters */}
          <div className="flex flex-col sm:flex-row gap-4 mb-8">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                placeholder="Search products, categories..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 shadow-card"
              />
            </div>
            <div className="flex gap-2">
              <Select value={selectedCategory || ""} onValueChange={(value) => setSelectedCategory(value === "all" ? null : value)}>
                <SelectTrigger className="w-[200px] shadow-card">
                  <Filter className="w-4 h-4 mr-2" />
                  <SelectValue placeholder="All Products" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Products</SelectItem>
                  {productNames.map((name) => (
                    <SelectItem key={name} value={name}>
                      {name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {(selectedCategory || searchTerm) && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setSelectedCategory(null);
                    setSearchTerm("");
                  }}
                  className="shadow-card"
                >
                  <X className="w-4 h-4" />
                  Clear
                </Button>
              )}
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card className="shadow-card">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Total Products</p>
                    <p className="text-2xl font-bold text-foreground">
                      {loading ? <Skeleton className="h-8 w-16" /> : pagination.count}
                    </p>
                  </div>
                  <Package className="w-8 h-8 text-primary" />
                </div>
              </CardContent>
            </Card>
            <Card className="shadow-card">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Available</p>
                    <p className="text-2xl font-bold text-success">
                      {loading ? <Skeleton className="h-8 w-16" /> : 
                        products.filter((p) => p.status.toLowerCase() === "available").length}
                    </p>
                  </div>
                  <CheckCircle className="w-8 h-8 text-success" />
                </div>
              </CardContent>
            </Card>
            <Card className="shadow-card">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Featured</p>
                    <p className="text-2xl font-bold text-warning">
                      {loading ? <Skeleton className="h-8 w-16" /> : 
                        products.filter((p) => p.is_featured).length}
                    </p>
                  </div>
                  <Star className="w-8 h-8 text-warning" />
                </div>
              </CardContent>
            </Card>
            <Card className="shadow-card">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Popular</p>
                    <p className="text-2xl font-bold text-destructive">
                      {loading ? <Skeleton className="h-8 w-16" /> : 
                        products.filter((p) => p.is_popular).length}
                    </p>
                  </div>
                  <AlertCircle className="w-8 h-8 text-destructive" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800">Error: {error}</p>
              <Button 
                variant="outline" 
                size="sm" 
                className="mt-2"
                onClick={() => fetchProducts({ page: currentPage, pageSize: 12 })}
              >
                Retry
              </Button>
            </div>
          )}

          {/* Products Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {loading ? (
              // Show skeletons while loading
              Array.from({ length: 6 }).map((_, index) => (
                <ProductSkeleton key={index} />
              ))
            ) : (
              filteredProducts.map((product) => {
                const isOwner = isAuthenticated && user?.id === product.owner;
                return (
                  <Card key={product.id} className="shadow-card hover:shadow-elegant transition-smooth">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <CardTitle className="text-lg font-semibold text-foreground mb-1">
                            {product.name}
                          </CardTitle>
                          <p className="text-sm text-muted-foreground mb-2">{product.category_name}</p>
                          <div className="flex gap-2 mb-2">
                            {getStatusBadge(product.status)}
                            {getConditionBadge(product.condition)}
                          </div>
                          {product.is_featured && (
                            <Badge className="bg-yellow-100 text-yellow-800">
                              <Star className="w-3 h-3 mr-1" />Featured
                            </Badge>
                          )}
                        </div>
                        <div className="w-20 h-20 bg-muted rounded-lg flex items-center justify-center overflow-hidden">
                          {product.main_image_url ? (
                            <img 
                              src={product.main_image_url} 
                              alt={product.name}
                              className="w-full h-full object-cover"
                              onError={(e) => {
                                e.currentTarget.src = '/placeholder.svg';
                              }}
                            />
                          ) : (
                            <Package className="w-8 h-8 text-muted-foreground" />
                          )}
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                        {product.short_description}
                      </p>

                      {/* Rating */}
                      <div className="flex items-center mb-4">
                        <div className="flex items-center">
                          {Array.from({ length: 5 }).map((_, i) => (
                            <Star
                              key={i}
                              className={`w-4 h-4 ${
                                i < Math.floor(product.average_rating)
                                  ? 'text-yellow-400 fill-current'
                                  : 'text-gray-300'
                              }`}
                            />
                          ))}
                        </div>
                        <span className="text-sm text-muted-foreground ml-2">
                          ({product.review_count} reviews)
                        </span>
                      </div>

                      {/* Pricing */}
                      <div className="space-y-2 mb-4">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-muted-foreground">Daily Rate:</span>
                          <span className="font-semibold text-foreground">
                            ${product.basic_pricing.daily_rate}
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-muted-foreground">Deposit:</span>
                          <span className="font-semibold text-foreground">
                            ${product.deposit_amount}
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-muted-foreground">Available:</span>
                          <span className="font-semibold text-foreground">
                            {product.available_quantity} units
                          </span>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex gap-2">
                        <Button 
                          variant="outline" 
                          size="sm" 
                          className="flex-1" 
                          onClick={() => navigate(`/products/${product.id}`)}
                        >
                          <Eye className="w-4 h-4 mr-1" />
                          View
                        </Button>
                        {isOwner && (
                          <Button 
                            variant="default" 
                            size="sm" 
                            className="flex-1"
                            onClick={() => navigate(`/products/edit/${product.id}`)}
                          >
                            <Edit className="w-4 h-4 mr-1" />
                            Edit
                          </Button>
                        )}
                        <Button
                          variant="success"
                          size="sm"
                          className="flex-1"
                          onClick={() => {
                            setSelectedProduct(product);
                            setDialogOpen(true);
                          }}
                        >
                          <Package className="w-4 h-4 mr-1" />
                          Add to Cart
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                );
              })
            )}
          </div>

          {/* Pagination */}
          {!loading && totalPages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1 || isFetching}
              >
                <ChevronLeft className="w-4 h-4 mr-1" />
                Previous
              </Button>
              
              <div className="flex items-center gap-1">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  const pageNum = i + 1;
                  return (
                    <Button
                      key={pageNum}
                      variant={pageNum === currentPage ? "default" : "outline"}
                      size="sm"
                      onClick={() => handlePageChange(pageNum)}
                    >
                      {pageNum}
                    </Button>
                  );
                })}
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages || isFetching}
              >
                <ChevronRight className="w-4 h-4 ml-1" />
                Next
              </Button>
            </div>
          )}
        </div>
      </div>
      {/* Date Selection Dialog for Add to Cart */}
      {selectedProduct && (
        <DateSelectionDialog
          isOpen={dialogOpen}
          onClose={() => {
            setDialogOpen(false);
            setSelectedProduct(null);
          }}
          onConfirm={(fromDate, toDate, quantity) => {
            addToCart(
              selectedProduct,
              quantity,
              fromDate,
              toDate,
              selectedProduct.basic_pricing.daily_rate
            );
          }}
          productName={selectedProduct.name}
          dailyRate={selectedProduct.basic_pricing.daily_rate}
        />
      )}
    </>
  );
};

export default Products;
