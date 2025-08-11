import { Navigation } from "@/components/Navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/contexts/AuthContext";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

const Profile = () => {
  const { user, signOut, signIn } = useAuth();

  const createAdminUser = () => {
    if (user) {
      const adminUser = {
        ...user,
        role: "admin" as const,
      };
      signIn(adminUser);
    }
  };

  const createNormalUser = () => {
    if (user) {
      const normalUser = {
        ...user,
        role: "user" as const,
      };
      signIn(normalUser);
    }
  };

  const getRoleBadge = (role: string) => {
    switch (role) {
      case "admin":
        return <Badge className="bg-destructive text-destructive-foreground">Admin</Badge>;
      case "user":
        return <Badge className="bg-primary text-primary-foreground">User</Badge>;
      default:
        return <Badge variant="secondary">Guest</Badge>;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <Card className="shadow-card">
          <CardHeader className="flex flex-col items-center gap-4">
            <Avatar className="h-20 w-20">
              <AvatarImage src="/avatar.png" alt="Avatar" />
              <AvatarFallback>{user?.name?.[0] ?? "U"}</AvatarFallback>
            </Avatar>
            <div className="text-center">
              <CardTitle className="text-2xl">Your Profile</CardTitle>
              <div className="text-sm text-muted-foreground mt-1">Manage your account details</div>
            </div>
          </CardHeader>
          <CardContent>
            {user ? (
              <div className="grid gap-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <div className="space-y-1">
                    <div className="text-sm text-muted-foreground">Name</div>
                    <div className="text-foreground font-medium">{user.name}</div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-sm text-muted-foreground">Email</div>
                    <div className="text-foreground font-medium break-all">{user.email}</div>
                  </div>
                  <div className="space-y-1 sm:col-span-2">
                    <div className="text-sm text-muted-foreground">Phone</div>
                    <div className="text-foreground font-medium">{user.phone ?? "—"}</div>
                  </div>
                  <div className="space-y-1 sm:col-span-2">
                    <div className="text-sm text-muted-foreground">Role</div>
                    <div className="flex items-center gap-2">
                      <span className="text-foreground font-medium">{user.role}</span>
                      {getRoleBadge(user.role)}
                    </div>
                  </div>
                </div>

                {/* Role Testing Buttons - Remove in production */}
                <div className="border-t pt-4">
                  <div className="text-sm text-muted-foreground mb-3">Testing: Change User Role</div>
                  <div className="flex gap-2">
                    <Button onClick={createNormalUser} variant="outline" size="sm">
                      Set as Normal User
                    </Button>
                    <Button onClick={createAdminUser} variant="outline" size="sm">
                      Set as Admin
                    </Button>
                  </div>
                </div>

                <div className="flex justify-end">
                  <Button onClick={signOut} variant="outline">Sign Out</Button>
                </div>
              </div>
            ) : (
              <div className="text-muted-foreground">You are not signed in.</div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Profile;


