"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import Cookies from "js-cookie";
import { useRouter, usePathname } from "next/navigation";
import { api } from "@/lib/api";

interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (token: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const token = Cookies.get("vision_token");
    if (token) {
      fetchUser(token);
    } else {
      setIsLoading(false);
      // Let's redirect users automatically away from protected routes if not logged in
      if (pathname !== "/login" && pathname !== "/") {
         router.push("/login");
      }
    }
  }, [pathname, router]);

  const fetchUser = async (token: string) => {
    try {
      // In a real app we would use an /users/me endpoint, but we created it!
      const res = await api.get("/users/me", {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(res.data);
    } catch (error) {
      console.error("Failed to load user", error);
      Cookies.remove("vision_token");
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (token: string) => {
    Cookies.set("vision_token", token, { expires: 7 }); // 7 days expiration
    await fetchUser(token);
    router.push("/dashboard");
  };

  const logout = () => {
    Cookies.remove("vision_token");
    setUser(null);
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
