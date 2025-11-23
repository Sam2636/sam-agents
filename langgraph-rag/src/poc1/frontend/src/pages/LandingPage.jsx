import FloatingLines from "../components/FloatingLines";

export default function LandingPage() {
  return (
    <div 
      style={{ width: "100%", height: "100vh", position: "relative", overflow: "hidden" }}
    >

      {/* 👇 ADD YOUR FLOATING LINES HERE */}
      <FloatingLines
        enabledWaves={['top', 'middle', 'bottom']}
        lineCount={[10, 15, 20]}
        lineDistance={[8, 6, 4]}
        bendRadius={5.0}
        bendStrength={-0.5}
        interactive={true}
        parallax={true}
      />

      {/* 👇 Your landing page content goes here */}
      <div 
        style={{ 
          position: "relative", 
          zIndex: 10, 
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          height: "100%",
          color: "white"
        }}
      >
        <h1>Your Landing Page</h1>

        <button
          onClick={() => window.location.href = "/chat"}
          style={{
            padding: "10px 20px",
            marginTop: "20px",
            background: "rgba(255,255,255,0.2)",
            border: "1px solid white",
            color: "white",
            borderRadius: "8px",
          }}
        >
          Go to Chat
        </button>
      </div>
    </div>
  );
}
