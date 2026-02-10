import React from "react";
import { Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import MainPage from "./pages/MainPage";
import SqlGenerationPage from "./pages/SqlGenerationPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/app" element={<MainPage />} />
      <Route path="/sql" element={<SqlGenerationPage />} />
    </Routes>
  );
}

export default App;
