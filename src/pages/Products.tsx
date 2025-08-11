import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Navigation } from "@/components/Navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
} from "lucide-react";
import { products as productsData } from "@/data/products";

const Products = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const navigate = useNavigate();

  const products = productsData;

  const getStatusBadge = (status: string) => {
    switch (status) {
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

  const filteredProducts = products.filter(
    (product) =>
      product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      product.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-foreground mb-2">Product Catalog</h1>
            <p className="text-muted-foreground">Manage your rental inventory and pricing</p>
          </div>
          <Button variant="hero" size="lg" className="mt-4 sm:mt-0">
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
          <Button variant="outline" className="shadow-card">
            <Filter className="w-4 h-4 mr-2" />
            Filters
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="shadow-card">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Total Products</p>
                  <p className="text-2xl font-bold text-foreground">{products.length}</p>
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
                    {products.filter((p) => p.status === "available").length}
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
                  <p className="text-sm text-muted-foreground mb-1">Currently Rented</p>
                  <p className="text-2xl font-bold text-warning">
                    {products.filter((p) => p.status === "rented").length}
                  </p>
                </div>
                <Clock className="w-8 h-8 text-warning" />
              </div>
            </CardContent>
          </Card>
          <Card className="shadow-card">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Maintenance</p>
                  <p className="text-2xl font-bold text-destructive">
                    {products.filter((p) => p.status === "maintenance").length}
                  </p>
                </div>
                <AlertCircle className="w-8 h-8 text-destructive" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Products Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map((product) => (
            <Card key={product.id} className="shadow-card hover:shadow-elegant transition-smooth">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg font-semibold text-foreground mb-1">
                      {product.name}
                    </CardTitle>
                    <p className="text-sm text-muted-foreground mb-2">{product.category}</p>
                    {getStatusBadge(product.status)}
                  </div>
                  <div className="w-20 h-20 bg-muted rounded-lg flex items-center justify-center">
                    <Package className="w-8 h-8 text-muted-foreground" />
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                  {product.description}
                </p>

                {/* Pricing */}
                <div className="space-y-2 mb-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Daily Rate:</span>
                    <span className="font-semibold text-foreground">${product.dailyRate}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Weekly Rate:</span>
                    <span className="font-semibold text-foreground">${product.weeklyRate}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Monthly Rate:</span>
                    <span className="font-semibold text-foreground">${product.monthlyRate}</span>
                  </div>
                </div>

                {/* Stock and Stats */}
                <div className="flex justify-between items-center mb-4 p-3 bg-muted rounded-lg">
                  <div className="text-center">
                    <p className="text-sm text-muted-foreground">Stock</p>
                    <p className="font-semibold text-foreground">{product.stock}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-muted-foreground">Total Rentals</p>
                    <p className="font-semibold text-foreground">{product.totalRentals}</p>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" className="flex-1" onClick={() => navigate(`/products/${product.id}`)}>
                    <Eye className="w-4 h-4 mr-1" />
                    View
                  </Button>
                  <Button variant="default" size="sm" className="flex-1">
                    <Edit className="w-4 h-4 mr-1" />
                    Edit
                  </Button>
                  <Button variant="hero" size="sm" className="flex-1">
                    <Calendar className="w-4 h-4 mr-1" />
                    Book
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Products;