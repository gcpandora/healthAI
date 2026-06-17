import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Layout from "./components/Layout";
import RequireAuth from "./components/RequireAuth";
import Dashboard from "./pages/Dashboard";
import Users from "./pages/Users";
import Exercises from "./pages/Exercises";
import Nutrition from "./pages/Nutrition";
import DataQuality from "./pages/DataQuality";
import Account from "./pages/Account";
import Login from "./pages/Login";

import NutritionAI from "./pages/NutritionAI";
import FitnessRecommendations from "./pages/FitnessRecommendations";
import MLPredictions from "./pages/MLPredictions";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<RequireAuth><Layout><Dashboard /></Layout></RequireAuth>} />
        <Route path="/users" element={<RequireAuth><Layout><Users /></Layout></RequireAuth>} />
        <Route path="/exercises" element={<RequireAuth><Layout><Exercises /></Layout></RequireAuth>} />
        <Route path="/nutrition" element={<RequireAuth><Layout><Nutrition /></Layout></RequireAuth>} />
        <Route path="/data-quality" element={<RequireAuth><Layout><DataQuality /></Layout></RequireAuth>} />
        <Route path="/account" element={<RequireAuth><Layout><Account /></Layout></RequireAuth>} />
        <Route path="/nutrition-ai" element={<RequireAuth><Layout><NutritionAI /></Layout></RequireAuth>} />
        <Route path="/fitness" element={<RequireAuth><Layout><FitnessRecommendations /></Layout></RequireAuth>} />
        <Route path="/ml-predictions" element={<RequireAuth><Layout><MLPredictions /></Layout></RequireAuth>} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}