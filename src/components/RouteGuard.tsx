import { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";

type RouteGuardProps = {
  children: ReactNode;
  requiredRole?: "admin" | "user" | "guest";
  fallbackPath?: string;
};

export const RouteGuard = ({ 
  children, 
  requiredRole = "guest", 
  fallbackPath = "/" 
}: RouteGuardProps) => {
  const { user, isAdmin, isUser } = useAuth();

  const hasAccess = () => {
    if (requiredRole === "guest") return true;
    if (requiredRole === "user" && (isUser || isAdmin)) return true;
    if (requiredRole === "admin" && isAdmin) return true;
    return false;
  };

  if (!hasAccess()) {
    return <Navigate to={fallbackPath} replace />;
  }

  return <>{children}</>;
};
