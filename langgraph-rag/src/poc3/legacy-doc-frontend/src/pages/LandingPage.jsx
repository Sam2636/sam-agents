import FloatingLines from "../components/FloatingLines";
import { useNavigate } from "react-router-dom";
import { Container, Typography, Button, Box, Stack } from "@mui/material";

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div
      style={{ width: "100%", height: "100vh", position: "relative", overflow: "hidden", backgroundColor: "#000" }}
    >

      {/* 👇 ADD YOUR FLOATING LINES HERE */}
      <div style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", zIndex: 0 }}>
        <FloatingLines
          enabledWaves={['top', 'middle', 'bottom']}
          lineCount={[10, 15, 20]}
          lineDistance={[8, 6, 4]}
          bendRadius={5.0}
          bendStrength={-0.5}
          interactive={true}
          parallax={true}
        />
      </div>

      {/* 👇 Your landing page content goes here */}
      <Container
        maxWidth="md"
        sx={{
          position: "relative",
          zIndex: 10,
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          color: "white",
          textAlign: "center"
        }}
      >
        <Stack spacing={4} alignItems="center">
          <Typography variant="h2" component="h1" fontWeight="bold" sx={{ textShadow: "0px 4px 20px rgba(0,0,0,0.5)" }}>
            Transform Legacy Code into Clear Documentation
          </Typography>

          <Typography
            variant="h5"
            component="p"
            sx={{
              maxWidth: "800px",
              color: "#fefffdff",
              textShadow: "0px 2px 10px rgba(0,0,0,0.5)",
              opacity: 0.9
            }}
          >
            AI-powered analysis to understand, document, and modernize your codebase.
            Upload your project or point to a repository to get started.
          </Typography>


          <Button
            variant="contained"
            size="large"
            onClick={() => navigate("/app")}
            sx={{
              mt: 4,
              px: 6,
              py: 2,
              fontSize: "1.2rem",
              borderRadius: "50px",
              textTransform: "none",
              background: "linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)",
              boxShadow: '0 3px 5px 2px rgba(33, 203, 243, .3)',
            }}
          >
            Get Started
          </Button>
        </Stack>
      </Container>
    </div>
  );
}
