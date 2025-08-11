import { useEffect, useState } from "react";
import { Navigation } from "@/components/Navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/hooks/useAuth";
import { useAppSelector } from "@/store/hooks";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { apiService } from "@/services/api";
import { toast } from "sonner";
import { Loader2, User, Mail, Phone, Shield, Calendar, CheckCircle, XCircle } from "lucide-react";

const Profile = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const [profileData, setProfileData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch profile data on component mount
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiService.getProfile();
        setProfileData(response.data);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch profile';
        setError(errorMessage);
        toast.error(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    if (isAuthenticated) {
      fetchProfile();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated]);

  const getRoleBadge = (role: string) => {
    switch (role?.toLowerCase()) {
      case "admin":
        return <Badge className="bg-destructive text-destructive-foreground">Admin</Badge>;
      case "user":
        return <Badge className="bg-primary text-primary-foreground">User</Badge>;
      default:
        return <Badge variant="secondary">Guest</Badge>;
    }
  };

  const getVerificationStatus = (verifiedAt: string | null) => {
    if (verifiedAt) {
      return (
        <div className="flex items-center text-green-600">
          <CheckCircle className="w-4 h-4 mr-1" />
          <span className="text-sm">Verified</span>
        </div>
      );
    } else {
      return (
        <div className="flex items-center text-red-600">
          <XCircle className="w-4 h-4 mr-1" />
          <span className="text-sm">Not Verified</span>
        </div>
      );
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
          <Card className="shadow-card">
            <CardContent className="p-6 text-center">
              <p className="text-muted-foreground">Please log in to view your profile.</p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <Card className="shadow-card">
          <CardHeader className="flex flex-col items-center gap-4">
            <Avatar className="h-20 w-20">
              <AvatarImage src="/avatar.png" alt="Avatar" />
              <AvatarFallback>
                {profileData?.user?.first_name?.[0] || user?.first_name?.[0] || "U"}
              </AvatarFallback>
            </Avatar>
            <div className="text-center">
              <CardTitle className="text-2xl">Your Profile</CardTitle>
              <div className="text-sm text-muted-foreground mt-1">Manage your account details</div>
            </div>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-16" />
                    <Skeleton className="h-6 w-32" />
                  </div>
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-16" />
                    <Skeleton className="h-6 w-40" />
                  </div>
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-16" />
                    <Skeleton className="h-6 w-32" />
                  </div>
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-16" />
                    <Skeleton className="h-6 w-24" />
                  </div>
                </div>
              </div>
            ) : error ? (
              <div className="text-center space-y-4">
                <p className="text-red-600">{error}</p>
                <Button 
                  onClick={() => window.location.reload()} 
                  variant="outline"
                >
                  Retry
                </Button>
              </div>
            ) : (
              <div className="grid gap-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <div className="space-y-1">
                    <div className="text-sm text-muted-foreground flex items-center">
                      <User className="w-4 h-4 mr-1" />
                      Full Name
                    </div>
                    <div className="text-foreground font-medium">
                      {profileData?.user?.prefix} {profileData?.user?.first_name} {profileData?.user?.last_name}
                    </div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-sm text-muted-foreground flex items-center">
                      <Mail className="w-4 h-4 mr-1" />
                      Email
                    </div>
                    <div className="text-foreground font-medium break-all">
                      {profileData?.user?.email || user?.email}
                    </div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-sm text-muted-foreground flex items-center">
                      <Phone className="w-4 h-4 mr-1" />
                      Phone Number
                    </div>
                    <div className="text-foreground font-medium">
                      {profileData?.user?.phone_number || user?.phone_number || "—"}
                    </div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-sm text-muted-foreground flex items-center">
                      <Shield className="w-4 h-4 mr-1" />
                      Role
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-foreground font-medium capitalize">
                        {profileData?.user?.user_role || "user"}
                      </span>
                      {getRoleBadge(profileData?.user?.user_role)}
                    </div>
                  </div>
                </div>

                {/* Verification Status */}
                <div className="border-t pt-4">
                  <h3 className="text-lg font-semibold mb-3">Verification Status</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="space-y-1">
                      <div className="text-sm text-muted-foreground">Email Verification</div>
                      {getVerificationStatus(profileData?.user?.email_verified_at)}
                    </div>
                    <div className="space-y-1">
                      <div className="text-sm text-muted-foreground">Phone Verification</div>
                      {getVerificationStatus(profileData?.user?.phone_verified_at)}
                    </div>
                  </div>
                </div>

                {/* Account Information */}
                <div className="border-t pt-4">
                  <h3 className="text-lg font-semibold mb-3">Account Information</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="space-y-1">
                      <div className="text-sm text-muted-foreground flex items-center">
                        <Calendar className="w-4 h-4 mr-1" />
                        Account Status
                      </div>
                      <div className="text-foreground font-medium">
                        {profileData?.user?.is_verified ? "Verified" : "Pending Verification"}
                      </div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-sm text-muted-foreground">User ID</div>
                      <div className="text-foreground font-medium text-sm break-all">
                        {profileData?.user?.id || user?.id}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex justify-end">
                  <Button onClick={logout} variant="outline">
                    Sign Out
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Profile;


