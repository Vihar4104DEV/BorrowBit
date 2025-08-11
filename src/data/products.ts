export type Product = {
  id: number;
  name: string;
  category: string;
  status: "available" | "rented" | "maintenance" | string;
  dailyRate: number;
  weeklyRate: number;
  monthlyRate: number;
  stock: number;
  totalRentals: number;
  image: string;
  description: string;
};

export const products: Product[] = [
  {
    id: 1,
    name: "Professional Camera Kit",
    category: "Photography",
    status: "available",
    dailyRate: 150,
    weeklyRate: 900,
    monthlyRate: 3200,
    stock: 5,
    totalRentals: 48,
    image: "/placeholder.svg",
    description: "Complete professional camera setup with lenses and accessories",
  },
  {
    id: 2,
    name: "Wedding Tent Large",
    category: "Event Equipment",
    status: "rented",
    dailyRate: 200,
    weeklyRate: 1200,
    monthlyRate: 4500,
    stock: 2,
    totalRentals: 32,
    image: "/placeholder.svg",
    description: "Large capacity wedding tent for outdoor events",
  },
  {
    id: 3,
    name: "Sound System Pro",
    category: "Audio",
    status: "maintenance",
    dailyRate: 300,
    weeklyRate: 1800,
    monthlyRate: 6500,
    stock: 3,
    totalRentals: 67,
    image: "/placeholder.svg",
    description: "Professional sound system with microphones and speakers",
  },
  {
    id: 4,
    name: "Luxury Car BMW X5",
    category: "Vehicles",
    status: "available",
    dailyRate: 180,
    weeklyRate: 1100,
    monthlyRate: 4000,
    stock: 1,
    totalRentals: 23,
    image: "/placeholder.svg",
    description: "Premium luxury vehicle for special occasions",
  },
  {
    id: 5,
    name: "Construction Tools Set",
    category: "Tools & Equipment",
    status: "available",
    dailyRate: 75,
    weeklyRate: 450,
    monthlyRate: 1600,
    stock: 8,
    totalRentals: 89,
    image: "/placeholder.svg",
    description: "Complete construction tools set for professional use",
  },
  {
    id: 6,
    name: "Party Lighting Package",
    category: "Event Equipment",
    status: "rented",
    dailyRate: 120,
    weeklyRate: 720,
    monthlyRate: 2500,
    stock: 4,
    totalRentals: 156,
    image: "/placeholder.svg",
    description: "Professional party lighting with LED panels and controls",
  },
];

export function getProductById(id: number): Product | undefined {
  return products.find((p) => p.id === id);
}
