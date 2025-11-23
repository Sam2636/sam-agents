import { BrowserRouter, Routes, Route } from "react-router-dom";
import Landingpage from "./pages/LandingPage";
import Chatpage from "./pages/ChatPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landingpage />} />
        <Route path="/chat" element={<Chatpage />} />
      </Routes>
    </BrowserRouter>
  );
}
