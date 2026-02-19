import { useNavigate } from "react-router-dom";
import { Container, Typography, Button, Box, Stack, Paper, Chip } from "@mui/material";
import bgImage from "../assets/background2.png";
import architectureImage from "../assets/architecture.png";

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <Box
      sx={{
        width: "100%",
        minHeight: "100vh",
        position: "relative",
        overflowX: "hidden",
        overflowY: "visible",
        backgroundColor: "#040a10"
      }}
    >
      <Box
        sx={{
          position: "fixed",
          inset: 0,
          backgroundImage: `url(${bgImage})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          opacity: 0.4,
          pointerEvents: "none",
          zIndex: 0
        }}
      />
      <Box
        sx={{
          position: "fixed",
          inset: 0,
          background:
            "radial-gradient(1200px 520px at 10% -10%, rgba(34,197,94,0.18), transparent 60%), radial-gradient(1000px 520px at 90% -20%, rgba(14,165,233,0.18), transparent 58%), linear-gradient(180deg, rgba(2,6,12,0.45), rgba(2,6,12,0.82))",
          pointerEvents: "none",
          zIndex: 0
        }}
      />

      <Container
        maxWidth="lg"
        sx={{
          position: "relative",
          zIndex: 10,
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "flex-start",
          color: "white",
          textAlign: "center",
          py: 8
        }}
      >
        <Stack
          spacing={4}
          alignItems="center"
          sx={{ width: "100%", minHeight: "82vh", justifyContent: "center" }}
        >
          <Chip
            label="AI Metadata + Lineage Copilot"
            sx={{
              bgcolor: "rgba(14,165,233,0.14)",
              color: "#c7f1ff",
              border: "1px solid rgba(125,211,252,0.35)"
            }}
          />
          <Typography
            variant="h2"
            component="h1"
            fontWeight="bold"
            sx={{
              textShadow: "0px 4px 20px rgba(0,0,0,0.45)",
              fontSize: { xs: "2rem", md: "3.3rem" }
            }}
          >
            High-Level SQL Generation for Data Processing and Warehousing
          </Typography>

          <Typography
            variant="h5"
            component="p"
            sx={{
              maxWidth: "800px",
              color: "rgba(236,253,245,0.92)",
              textShadow: "0px 2px 10px rgba(0,0,0,0.35)",
              opacity: 0.9
            }}
          >
            Generate production-ready SQL from lineage, metadata, and business intent.
            Accelerate ETL design, governance, and warehouse optimization with an AI copiloting workflow.
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
                background: "linear-gradient(90deg, #0ea5e9 0%, #22c55e 100%)",
                boxShadow: "0 10px 30px rgba(14,165,233,0.24)"
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
                borderColor: "rgba(148, 251, 221, 0.55)",
                color: "#d6fff3"
              }}
            >
              Open Platform
            </Button>
          </Box>

          <Typography variant="body2" sx={{ color: "rgba(198,232,242,0.75)" }}>
            Scroll down to view architecture
          </Typography>
        </Stack>

        <Paper
          elevation={0}
          sx={{
            width: "100%",
            mt: 2,
            p: { xs: 2, md: 2.5 },
            borderRadius: 3,
            bgcolor: "rgba(8,16,26,0.72)",
            border: "1px solid rgba(125,211,252,0.24)",
            display: "grid",
            gridTemplateColumns: { xs: "1fr", md: "1.2fr 0.8fr" },
            gap: 2.5,
            alignItems: "center",
            textAlign: "left",
            mb: 6
          }}
        >
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 700, mb: 1.2, color: "#d7f5ff" }}>
              Platform Architecture
            </Typography>
            <Typography variant="body1" sx={{ color: "rgba(230,245,255,0.9)", mb: 1.2 }}>
              Unified backend for ingestion, graph lineage, and SQL agent orchestration.
              Real-time metadata flows into Neo4j, then powers lineage visualization and SQL generation.
            </Typography>
            <Stack direction="row" spacing={1} useFlexGap sx={{ flexWrap: "wrap" }}>
              <Chip label="Neo4j Lineage" size="small" sx={{ bgcolor: "rgba(34,197,94,0.18)", color: "#c8ffe3" }} />
              <Chip label="Bulk Metadata APIs" size="small" sx={{ bgcolor: "rgba(14,165,233,0.18)", color: "#d2f3ff" }} />
              <Chip label="SQL Agent" size="small" sx={{ bgcolor: "rgba(59,130,246,0.18)", color: "#d8e8ff" }} />
            </Stack>
          </Box>
          <Box
            component="img"
            src={architectureImage}
            alt="Platform architecture"
            sx={{
              width: "100%",
              borderRadius: 2,
              border: "1px solid rgba(125,211,252,0.28)",
              boxShadow: "0 14px 34px rgba(0,0,0,0.32)"
            }}
          />
        </Paper>
      </Container>
    </Box>
  );
}
