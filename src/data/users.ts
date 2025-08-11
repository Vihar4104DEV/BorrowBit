import { AuthUser } from "@/contexts/AuthContext";

export const dummyUsers: AuthUser[] = [
  {
    id: "1",
    name: "Admin User",
    email: "admin@example.com",
    phone: "+1234567890",
    role: "admin",
  },
  {
    id: "2",
    name: "Normal User",
    email: "user@example.com",
    phone: "+0987654321",
    role: "user",
  },
  {
    id: "3",
    name: "John Doe",
    email: "john@example.com",
    phone: "+1122334455",
    role: "user",
  },
];

export const getDummyUserByEmail = (email: string): AuthUser | undefined => {
  return dummyUsers.find(user => user.email === email);
};

export const getDummyUserById = (id: string): AuthUser | undefined => {
  return dummyUsers.find(user => user.id === id);
};
