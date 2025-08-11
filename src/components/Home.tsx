import { Button } from "@/components/ui/button";
import { 
  Calendar, 
  Package, 
  Users, 
  TrendingUp, 
  CheckCircle, 
  ArrowRight,
  Zap,
  Shield,
  Clock,
  Truck
} from "lucide-react";
import { useNavigate } from "react-router-dom";

export const Hero = () => {
  const navigate = useNavigate();
  
  const features = [
    {
      icon: Calendar,
      title: "Smart Scheduling",
      description: "Automated pickup & return scheduling with real-time tracking"
    },
    {
      icon: Package,
      title: "Inventory Management",
      description: "Complete product lifecycle management with availability tracking"
    },
    {
      icon: Users,
      title: "Customer Portal",
      description: "Self-service booking platform for your customers"
    },
    {
      icon: TrendingUp,
      title: "Advanced Analytics",
      description: "Comprehensive reports and business insights"
    }
  ];

  const benefits = [
    "Automated rental quotations & contracts",
    "Multi-tier pricing management",
    "Payment gateway integration",
    "Late return fee automation",
    "Real-time notifications",
    "Mobile-responsive design"
  ];

  return (
    <div className="relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 gradient-hero opacity-5"></div>
      <div className="absolute top-20 left-10 w-72 h-72 bg-primary/10 rounded-full blur-3xl animate-float"></div>
      <div className="absolute bottom-20 right-10 w-96 h-96 bg-accent/10 rounded-full blur-3xl animate-float" style={{ animationDelay: "1s" }}></div>
      
      {/* Hero Section */}
      <section className="relative pt-20 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center animate-fade-in">
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-primary/10 text-primary mb-8">
              <Zap className="w-4 h-4 mr-2" />
              <span className="text-sm font-medium">Complete Rental Management Solution</span>
            </div>
            
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground mb-6 leading-tight">
              Streamline Your{" "}
              <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                Rental Business
              </span>
              <br />
              Like Never Before
            </h1>
            
            <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto leading-relaxed">
              From quotations to returns, manage your entire rental operation with our 
              comprehensive platform. Automate bookings, track inventory, and delight 
              customers with seamless experiences.
            </p>
            
            {/* <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Button variant="hero" size="xl" className="group">
                Start Free Trial
                <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
              <Button variant="outline" size="xl" className="group">
                Watch Demo
                <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
            </div> */}

            {/* Trust Indicators */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-6 text-sm text-muted-foreground">
              <div className="flex items-center">
                <Shield className="w-4 h-4 mr-2 text-success" />
                Enterprise Security
              </div>
              <div className="flex items-center">
                <Clock className="w-4 h-4 mr-2 text-success" />
                24/7 Support
              </div>
              <div className="flex items-center">
                <CheckCircle className="w-4 h-4 mr-2 text-success" />
                No Setup Fees
              </div>
            </div>
            
            {/* Quick Access for Delivery Partners */}
            <div className="mt-8 p-4 bg-primary/5 rounded-lg border border-primary/20">
              <div className="text-center">
                <h3 className="text-lg font-semibold text-foreground mb-2">Are you a Delivery Partner?</h3>
                <p className="text-sm text-muted-foreground mb-4">Access your delivery dashboard to manage assignments and track deliveries</p>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => navigate("/delivery-partner")}
                  className="group"
                >
                  <Truck className="w-4 h-4 mr-2" />
                  Go to Delivery Dashboard
                  <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="relative py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16 animate-fade-in">
            <h2 className="text-3xl sm:text-4xl font-bold text-foreground mb-4">
              Everything You Need to Manage Rentals
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Powerful features designed to streamline every aspect of your rental business
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div
                  key={index}
                  className="bg-card rounded-lg p-6 shadow-card hover:shadow-elegant transition-smooth animate-slide-up border border-border/50"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <div className="w-12 h-12 gradient-primary rounded-lg flex items-center justify-center mb-4">
                    <Icon className="w-6 h-6 text-primary-foreground" />
                  </div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-muted-foreground text-sm leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>

          {/* Benefits Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="animate-fade-in">
              <h3 className="text-2xl sm:text-3xl font-bold text-foreground mb-6">
                Why Choose Borrowbit?
              </h3>
              <div className="space-y-4">
                {benefits.map((benefit, index) => (
                  <div key={index} className="flex items-center">
                    <CheckCircle className="w-5 h-5 text-success mr-3 flex-shrink-0" />
                    <span className="text-muted-foreground">{benefit}</span>
                  </div>
                ))}
              </div>
              <Button variant="default" size="lg" className="mt-8">
                Learn More About Features
              </Button>
            </div>
            
            <div className="animate-slide-up">
              <div className="gradient-card rounded-2xl p-8 shadow-elegant">
                <div className="text-center">
                  <div className="text-4xl font-bold text-primary mb-2">99.9%</div>
                  <div className="text-muted-foreground mb-4">Uptime Guarantee</div>
                  
                  <div className="grid grid-cols-2 gap-6 mt-8">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-accent">24/7</div>
                      <div className="text-sm text-muted-foreground">Support</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-success">500+</div>
                      <div className="text-sm text-muted-foreground">Happy Clients</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};