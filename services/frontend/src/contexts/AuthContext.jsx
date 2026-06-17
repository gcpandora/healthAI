import { createContext, useContext, useState, useEffect } from "react";
import { authAPI } from "../services/api";

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing session on app load
    const token = localStorage.getItem("authToken");
    const userData = localStorage.getItem("userData");

    if (token && userData) {
      try {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
      } catch (error) {
        console.error("Error parsing stored user data:", error);
        localStorage.removeItem("authToken");
        localStorage.removeItem("userData");
      }
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const response = await authAPI.login(email, password);
      const { access_token, user_id, username, role } = response.data;
      const userData = { id: user_id, username, role, email };

      localStorage.setItem("authToken", access_token);
      localStorage.setItem("userData", JSON.stringify(userData));

      setUser(userData);
      return { success: true };
    } catch (error) {
      // Fallback local user store when backend not available
      const localUsers = JSON.parse(localStorage.getItem("localUsers") || "[]");
      const found = localUsers.find((u) => u.email === email && u.password === password);
      if (found) {
        const token = "local-token";
        localStorage.setItem("authToken", token);
        localStorage.setItem("userData", JSON.stringify(found));
        setUser(found);
        return { success: true };
      }

      return {
        success: false,
        error: error.response?.data?.detail || "Login failed",
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await authAPI.register(userData);
      const { access_token, user: newUser } = response.data;

      localStorage.setItem("authToken", access_token);
      localStorage.setItem("userData", JSON.stringify(newUser));

      setUser(newUser);

      // Add to local fallback account list
      const localUsers = JSON.parse(localStorage.getItem("localUsers") || "[]");
      localUsers.push(newUser);
      localStorage.setItem("localUsers", JSON.stringify(localUsers));

      return { success: true };
    } catch (error) {
      // fallback to local storage only mode
      const localUsers = JSON.parse(localStorage.getItem("localUsers") || "[]");
      const exists = localUsers.some((u) => u.email === userData.email);
      if (exists) {
        return { success: false, error: "User already exists" };
      }

      const localUser = {
        id: Date.now(),
        first_name: userData.first_name,
        last_name: userData.last_name,
        email: userData.email,
        password: userData.password,
        gender: userData.gender,
        weight: userData.weight,
        height: userData.height,
        plan: userData.plan,
      };

      localUsers.push(localUser);
      localStorage.setItem("localUsers", JSON.stringify(localUsers));
      localStorage.setItem("authToken", "local-token");
      localStorage.setItem("userData", JSON.stringify(localUser));
      setUser(localUser);

      return { success: true };
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      // Ignore logout errors from backend
    }

    localStorage.removeItem("authToken");
    localStorage.removeItem("userData");
    setUser(null);
  };

  const updateProfile = async (updates) => {
    try {
      const response = await authAPI.updateProfile(updates);
      const updatedUser = { ...user, ...updates };
      localStorage.setItem("userData", JSON.stringify(updatedUser));
      setUser(updatedUser);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || "Update failed",
      };
    }
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    updateProfile,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};