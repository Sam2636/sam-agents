// src/pages/LandingPage.jsx
import { useNavigate } from "react-router-dom";

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col justify-center items-center bg-gray-50 text-gray-900 p-6">
      <h1 className="text-4xl font-bold mb-4">Welcome to Spec-Driven AI Agent</h1>
      <p className="text-lg text-gray-600 max-w-xl text-center mb-8">
        Your unified assistant for healthcare, finance, and appointment workflows. 
        Powered by LangGraph and human-in-the-loop.
      </p>

      <button
        onClick={() => navigate("/chat")}
        className="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition"
      >
        Start Chat
      </button>
    </div>
  );
}
