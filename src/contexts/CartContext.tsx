import { createContext, useContext, useState, ReactNode } from "react";
import { getProductById } from "@/data/products";

export type CartItem = {
  id: string;
  productId: number;
  product?: any;
  quantity: number;
  fromDate: string;
  toDate: string;
  dailyRate: number;
};

type CartContextValue = {
  cartItems: CartItem[];
  addToCart: (product: any, quantity: number, fromDate: string, toDate: string, dailyRate: number) => void;
  removeFromCart: (itemId: string) => void;
  updateQuantity: (itemId: string, quantity: number) => void;
  clearCart: () => void;
  getCartTotal: () => number;
  getCartItemCount: () => number;
};

const CartContext = createContext<CartContextValue | undefined>(undefined);

export function CartProvider({ children }: { children: ReactNode }) {
  const [cartItems, setCartItems] = useState<CartItem[]>([]);

  const addToCart = (product: any, quantity: number, fromDate: string, toDate: string, dailyRate: number) => {
    setCartItems(prev => {
      // Check if item already exists in cart
      const existingItemIndex = prev.findIndex(item => 
        item.productId === product.id && 
        item.fromDate === fromDate && 
        item.toDate === toDate
      );

      if (existingItemIndex !== -1) {
        // Update existing item quantity
        const updatedItems = [...prev];
        updatedItems[existingItemIndex] = {
          ...updatedItems[existingItemIndex],
          quantity: updatedItems[existingItemIndex].quantity + quantity
        };
        return updatedItems;
      } else {
        // Add new item
        const newItem: CartItem = {
          id: crypto.randomUUID(),
          productId: product.id,
          product,
          quantity,
          fromDate,
          toDate,
          dailyRate
        };
        return [...prev, newItem];
      }
    });
  };

  const removeFromCart = (itemId: string) => {
    setCartItems(prev => prev.filter(item => item.id !== itemId));
  };

  const updateQuantity = (itemId: string, quantity: number) => {
    if (quantity < 1) return;
    setCartItems(prev => 
      prev.map(item => 
        item.id === itemId ? { ...item, quantity } : item
      )
    );
  };

  const clearCart = () => {
    setCartItems([]);
  };

  const getCartTotal = () => {
    return cartItems.reduce((total, item) => {
      const from = new Date(item.fromDate);
      const to = new Date(item.toDate);
      const days = Math.ceil(Math.abs(to.getTime() - from.getTime()) / (1000 * 60 * 60 * 24)) || 1;
      return total + (item.quantity * item.dailyRate * days);
    }, 0);
  };

  const getCartItemCount = () => {
    return cartItems.reduce((count, item) => count + item.quantity, 0);
  };

  const value: CartContextValue = {
    cartItems,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    getCartTotal,
    getCartItemCount,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used within CartProvider");
  return ctx;
}
