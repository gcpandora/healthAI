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

// ── Réseau social (MSPR3) ─────────────────────────────────────────────────────
import Feed from "./pages/Feed";
import CreatePost from "./pages/CreatePost";
import SocialProfile from "./pages/SocialProfile";

// ── Messagerie instantanée ────────────────────────────────────────────────────
import Chat from "./pages/Chat";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />

        {/* ── Dashboard & Admin ── */}
        <Route path="/"             element={<RequireAuth><Layout><Dashboard /></Layout></RequireAuth>} />
        <Route path="/users"        element={<RequireAuth><Layout><Users /></Layout></RequireAuth>} />
        <Route path="/exercises"    element={<RequireAuth><Layout><Exercises /></Layout></RequireAuth>} />
        <Route path="/nutrition"    element={<RequireAuth><Layout><Nutrition /></Layout></RequireAuth>} />
        <Route path="/data-quality" element={<RequireAuth><Layout><DataQuality /></Layout></RequireAuth>} />
        <Route path="/account"      element={<RequireAuth><Layout><Account /></Layout></RequireAuth>} />

        {/* ── IA & ML ── */}
        <Route path="/nutrition-ai"   element={<RequireAuth><Layout><NutritionAI /></Layout></RequireAuth>} />
        <Route path="/fitness"        element={<RequireAuth><Layout><FitnessRecommendations /></Layout></RequireAuth>} />
        <Route path="/ml-predictions" element={<RequireAuth><Layout><MLPredictions /></Layout></RequireAuth>} />

        {/* ── Réseau social ── */}
        <Route path="/feed"           element={<RequireAuth><Layout><Feed /></Layout></RequireAuth>} />
        <Route path="/create-post"    element={<RequireAuth><Layout><CreatePost /></Layout></RequireAuth>} />
        <Route path="/social-profile" element={<RequireAuth><Layout><SocialProfile /></Layout></RequireAuth>} />

        {/* ── Messagerie ── */}
        {/*
          NOTE : Chat utilise toute la hauteur dispo (calc(100vh - header)).
          Le Layout doit avoir overflow:hidden sur le content wrapper.
          Si ce n'est pas le cas, ajouter dans Layout.jsx :
            <main style={{ flex: 1, overflow: 'hidden' }}>
        */}
        <Route path="/chat"           element={<RequireAuth><Layout><Chat /></Layout></RequireAuth>} />

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
