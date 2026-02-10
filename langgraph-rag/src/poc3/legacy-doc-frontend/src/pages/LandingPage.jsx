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
            High-Level SQL Generation for Data Processing and Warehousing
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
            Generate production-ready SQL from lineage, metadata, and business
            intent. Accelerate ETL design, governance, and warehouse
            optimization with an AI copiloting workflow.
          </Typography>


          <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap", mt: 1 }}>
                      <Button
                        variant="contained"
                        size="large"
                        onClick={() => navigate("/sql")}
                        sx={{
                          px: 6,
                          py: 2,
                          fontSize: "1.1rem",
                          borderRadius: "50px",
                          textTransform: "none",
                          background: "linear-gradient(90deg, #00c6ff 0%, #00ffb2 100%)",
                          boxShadow: "0 10px 30px rgba(0, 255, 200, 0.25)"
                        }}
                      >
                        Launch SQL Studio
                      </Button>
                      <Button
                        variant="outlined"
                        size="large"
                        onClick={() => navigate("/app")}
                        sx={{
                          px: 6,
                          py: 2,
                          fontSize: "1.1rem",
                          borderRadius: "50px",
                          textTransform: "none",
                          borderColor: "rgba(255,255,255,0.5)",
                          color: "#e7f6ff"
                        }}
                      >
                        Open Platform
                      </Button>
                    </Box>
        </Stack>
      </Container>
    </div>
  );
}
