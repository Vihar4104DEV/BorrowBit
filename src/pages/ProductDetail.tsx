import { useEffect, useMemo, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { Navigation } from "@/components/Navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { 
  Calendar as CalendarIcon, 
  Heart, 
  Minus, 
  Plus, 
  Package, 
  Star,
  Edit,
  ArrowLeft,
  Loader2,
  CheckCircle,
  AlertCircle,
  MapPin,
  Scale,
  Ruler,
  Palette,
  HardHat,
  Tag,
  Settings,
  Shield,
  Clock,
  Calendar,
  DollarSign,
  Truck,
  Warehouse,
  FileText,
  Share2
} from "lucide-react";
import { useProductDetails } from "@/hooks/useProductDetails";
import { useAuth } from "@/hooks/useAuth";
import BookingModal from "@/components/BookingModal";

const ProductDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { product, loading, error, fetchProductDetails, isFetching } = useProductDetails();
  const { user, isAuthenticated } = useAuth();

  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [qty, setQty] = useState(1);
  const [coupon, setCoupon] = useState("");
  const [isBookingModalOpen, setIsBookingModalOpen] = useState(false);

  // Check if current user is the owner of the product
  const isOwner = useMemo(() => {
    return isAuthenticated && user?.id === product?.owner;
  }, [isAuthenticated, user?.id, product?.owner]);

  useEffect(() => {
    if (id) {
      fetchProductDetails(id);
    }
  }, [id, fetchProductDetails]);

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

  if (loading || isFetching) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center gap-2 mb-6">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-4" />
            <Skeleton className="h-4 w-32" />
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
            <Card className="shadow-card">
              <CardContent className="p-6">
                <Skeleton className="w-full aspect-square rounded-xl" />
                <div className="mt-6 flex justify-center">
                  <Skeleton className="h-10 w-40" />
                </div>
              </CardContent>
            </Card>
            <div className="space-y-6">
              <Skeleton className="h-8 w-3/4" />
              <Skeleton className="h-6 w-1/2" />
              <Skeleton className="h-20 w-full" />
              <Skeleton className="h-12 w-full" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
          <div className="text-center space-y-4">
            <Package className="w-16 h-16 text-muted-foreground mx-auto" />
            <h2 className="text-2xl font-bold text-foreground">Product Not Found</h2>
            <p className="text-muted-foreground">
              {error || "The product you're looking for doesn't exist."}
            </p>
            <div className="flex gap-4 justify-center">
              <Button variant="outline" onClick={() => navigate(-1)}>
                <ArrowLeft className="w-4 h-4 mr-2" />
                Go Back
              </Button>
              <Button onClick={() => navigate('/products')}>
                Browse Products
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb */}
        <div className="text-sm text-muted-foreground mb-6 flex items-center gap-2">
          <Link to="/products" className="underline hover:text-foreground">All Products</Link>
          <span>/</span>
          <span className="text-foreground">{product.name}</span>
        </div>

                  <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 lg:gap-10">
            {/* Left: Image and details */}
            <div className="space-y-4 lg:space-y-6">
            <Card className="shadow-card">
              <CardContent className="p-6">
                <div className="w-full aspect-square rounded-xl bg-muted flex items-center justify-center overflow-hidden">
                  {product.main_image ? (
                    <img 
                      src={product.main_image} 
                      alt={product.name} 
                      className="w-full h-full object-cover rounded-xl"
                      onError={(e) => {
                        e.currentTarget.src = '/placeholder.svg';
                      }}
                    />
                  ) : (
                    <Package className="w-16 h-16 text-muted-foreground" />
                  )}
                </div>
                
                {/* Product badges */}
                <div className="mt-4 flex flex-wrap gap-2">
                  {getStatusBadge(product.status)}
                  {getConditionBadge(product.condition)}
                  {product.is_featured && (
                    <Badge className="bg-yellow-100 text-yellow-800">
                      <Star className="w-3 h-3 mr-1" />Featured
                    </Badge>
                  )}
                  {product.is_popular && (
                    <Badge className="bg-purple-100 text-purple-800">
                      <Heart className="w-3 h-3 mr-1" />Popular
                    </Badge>
                  )}
                </div>

                <div className="mt-6 flex justify-center">
                  <Button variant="outline" className="rounded-full px-8" size="lg">
                    <Heart className="w-4 h-4 mr-2" />
                    Add to wish list
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Product description */}
            <Card className="shadow-card">
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold mb-4">Description</h3>
                <p className="text-foreground leading-relaxed mb-4">{product.short_description}</p>
                <p className="text-foreground leading-relaxed">{product.description}</p>
              </CardContent>
            </Card>

            {/* Specifications */}
            <Card className="shadow-card">
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold mb-4">Specifications</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="flex items-center gap-2">
                    <Scale className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Weight:</span>
                    <span className="text-sm font-medium">{product.specifications.weight}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Ruler className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Dimensions:</span>
                    <span className="text-sm font-medium">{product.specifications.dimensions}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Palette className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Color:</span>
                    <span className="text-sm font-medium">{product.specifications.color}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <HardHat className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Material:</span>
                    <span className="text-sm font-medium">{product.specifications.material}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Tag className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Brand:</span>
                    <span className="text-sm font-medium">{product.specifications.brand}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Settings className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Model:</span>
                    <span className="text-sm font-medium">{product.specifications.model}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Features */}
            {product.features && product.features.length > 0 && (
              <Card className="shadow-card">
                <CardContent className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Features</h3>
                  <div className="flex flex-wrap gap-2">
                    {product.features.map((feature, index) => (
                      <Badge key={index} variant="outline">
                        {feature}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

                      {/* Right: Details and booking */}
            <div className="space-y-4 lg:space-y-6">
            {/* Header with edit button for owner */}
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-foreground mb-2">{product.name}</h1>
                <p className="text-muted-foreground">SKU: {product.sku}</p>
              </div>
              {isOwner && (
                <Button 
                  variant="outline" 
                  onClick={() => navigate(`/products/edit/${product.id}`)}
                >
                  <Edit className="w-4 h-4 mr-2" />
                  Edit Product
                </Button>
              )}
            </div>

            {/* Category and owner info */}
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <span>Category: {product.category.name}</span>
              <span>•</span>
              <span>Owner: {product.owner_name}</span>
            </div>

            {/* Pricing */}
            <Card className="shadow-card">
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold mb-4">Pricing</h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-muted-foreground">Deposit Amount:</span>
                    <span className="font-semibold">${product.deposit_amount}</span>
                  </div>
                  {product.pricing_rules && product.pricing_rules.length > 0 && (
                    product.pricing_rules.slice(0, 3).map((rule, index) => (
                      <div key={index} className="flex justify-between items-center">
                        <span className="text-muted-foreground capitalize">
                          {rule.duration_type.toLowerCase()} Rate:
                        </span>
                        <span className="font-semibold">
                          ${rule.price_per_unit}
                        </span>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Availability */}
            <Card className="shadow-card">
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold mb-4">Availability</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm text-muted-foreground">Available:</span>
                    <p className="font-semibold">{product.available_quantity} units</p>
                  </div>
                  <div>
                    <span className="text-sm text-muted-foreground">Total:</span>
                    <p className="font-semibold">{product.total_quantity} units</p>
                  </div>
                  <div>
                    <span className="text-sm text-muted-foreground">Minimum:</span>
                    <p className="font-semibold">{product.minimum_quantity} unit</p>
                  </div>
                  <div>
                    <span className="text-sm text-muted-foreground">Reserved:</span>
                    <p className="font-semibold">{product.reserved_quantity} units</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Rental Information */}
            <Card className="shadow-card">
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold mb-4">Rental Information</h3>
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Shield className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Rentable:</span>
                    <span className="font-medium">{product.is_rentable ? 'Yes' : 'No'}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Min Duration:</span>
                    <span className="font-medium">{product.minimum_rental_duration} hours</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Max Duration:</span>
                    <span className="font-medium">{product.maximum_rental_duration} hours</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Location and Storage */}
            <Card className="shadow-card">
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold mb-4">Location & Storage</h3>
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Warehouse className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Warehouse:</span>
                    <span className="font-medium">{product.warehouse_location}</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <FileText className="w-4 h-4 text-muted-foreground mt-0.5" />
                    <div>
                      <span className="text-sm text-muted-foreground">Storage Requirements:</span>
                      <p className="text-sm font-medium">{product.storage_requirements}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Booking Section */}
            <Card className="shadow-card border-2 border-primary/10">
              <CardHeader className="bg-gradient-to-r from-primary/5 to-primary/10 border-b">
                <CardTitle className="flex items-center gap-3 text-primary">
                  <div className="p-2 bg-primary rounded-lg">
                    <Calendar className="w-5 h-5 text-white" />
                  </div>
                  Book This Product
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                <div className="space-y-6">
                  {/* Quick Info */}
                  <div className="grid grid-cols-2 gap-4 p-4 bg-blue-50 rounded-lg">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        ${product.pricing_rules?.[0]?.daily_rate || '0'}
                      </div>
                      <div className="text-sm text-blue-600">Daily Rate</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {product.available_quantity}
                      </div>
                      <div className="text-sm text-green-600">Available</div>
                    </div>
                  </div>

                  {/* Features Highlight */}
                  <div className="space-y-3">
                    <h4 className="font-semibold text-foreground">Why Choose This Product?</h4>
                    <div className="space-y-2">
                      {product.is_featured && (
                        <div className="flex items-center gap-2 text-sm">
                          <Star className="w-4 h-4 text-yellow-500" />
                          <span>Featured product with premium quality</span>
                        </div>
                      )}
                      {product.is_popular && (
                        <div className="flex items-center gap-2 text-sm">
                          <Heart className="w-4 h-4 text-red-500" />
                          <span>Popular choice among customers</span>
                        </div>
                      )}
                      <div className="flex items-center gap-2 text-sm">
                        <Shield className="w-4 h-4 text-green-500" />
                        <span>Secure deposit: ${product.deposit_amount}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <Truck className="w-4 h-4 text-blue-500" />
                        <span>Flexible rental duration</span>
                      </div>
                    </div>
                  </div>

                  {/* Book Now Button */}
                  <Button 
                    className="w-full h-12 text-lg font-semibold bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70" 
                    size="lg"
                    onClick={() => setIsBookingModalOpen(true)}
                  >
                    <Calendar className="w-5 h-5 mr-2" />
                    Book Now - Start Your Rental
                  </Button>

                  {/* Trust Indicators */}
                  <div className="flex items-center justify-center gap-4 text-sm text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span>Secure Payment</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Shield className="w-4 h-4 text-blue-500" />
                      <span>24/7 Support</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Truck className="w-4 h-4 text-purple-500" />
                      <span>Fast Delivery</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Terms and share */}
            <Card className="shadow-card">
              <CardContent className="p-6">
                <div className="space-y-4">
                  <div>
                    <div className="font-semibold text-foreground mb-2">Terms & Conditions</div>
                    <ul className="text-sm text-muted-foreground list-disc pl-5 space-y-1">
                      <li>All rentals are subject to availability.</li>
                      <li>Security deposit of ${product.deposit_amount} required.</li>
                      <li>Late returns will incur additional charges.</li>
                      <li>Minimum rental duration: {product.minimum_rental_duration} hours</li>
                    </ul>
                  </div>
                  <div>
                    <div className="font-semibold text-foreground mb-2">Share:</div>
                    <Button variant="outline" size="sm">
                      <Share2 className="w-4 h-4 mr-2" />
                      Share Product
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Booking Modal */}
      <BookingModal
        isOpen={isBookingModalOpen}
        onClose={() => setIsBookingModalOpen(false)}
        product={product}
      />
    </div>
  );
};

export default ProductDetail;
