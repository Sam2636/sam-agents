import React, { useEffect, useMemo, useState } from "react";
import {
  Container,
  Typography,
  Box,
  Paper,
  Stack,
  Divider,
  Button,
  CssBaseline,
  IconButton,
  ThemeProvider,
  createTheme
} from "@mui/material";
import {
  Brightness4,
  Brightness7,
  Refresh
} from "@mui/icons-material";
import { Link } from "react-router-dom";
import MetadataIngestDialog from "../components/MetadataIngestDialog";
import LineageGraph from "../components/LineageGraph";
import LineageGraphPlaceholder from "../components/LineageGraphPlaceholder";
import MetricCard from "../components/MetricCard";
import { fetchGraphMetrics } from "../services/api";

export default function MainPage() {
  const [openIngest, setOpenIngest] = useState(false);
  const [refreshGraph, setRefreshGraph] = useState(false);
  const [mode, setMode] = useState("dark");
  const [metrics, setMetrics] = useState({
    layers: [],
    summary: { layers: 0, tables: 0, versions: 0, columns: 0 }
  });

  useEffect(() => {
    let isActive = true;
    const loadMetrics = async () => {
      try {
        const res = await fetchGraphMetrics();
        if (isActive) setMetrics(res.data);
      } catch (err) {
        console.error("Graph metrics fetch failed", err);
      }
    };

    loadMetrics();
    const id = setInterval(loadMetrics, 5000);
    return () => {
      isActive = false;
      clearInterval(id);
    };
  }, []);

  const findLayer = (layerName) =>
    metrics.layers.find(l => l.layer === layerName) || {
      tables: 0,
      versions: 0,
      columns: 0
    };

  const odp = findLayer("ODP");
  const fdp = findLayer("FDP");
  const cdp = findLayer("CDP");

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          primary: { main: mode === "dark" ? "#1ed760" : "#0b5fff" },
          secondary: { main: mode === "dark" ? "#0b5fff" : "#1ed760" },
          background: {
            default: mode === "dark" ? "#0b0f0e" : "#f6f9ff",
            paper: mode === "dark" ? "#111716" : "#ffffff"
          },
          text: {
            primary: mode === "dark" ? "#f4f7f6" : "#0f1a2b",
            secondary: mode === "dark" ? "#b8c2bd" : "#51607a"
          }
        },
        shape: { borderRadius: 14 },
        typography: {
          fontFamily:
            '"Poppins","Montserrat","Segoe UI","Helvetica Neue",Arial,sans-serif'
        }
      }),
    [mode]
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: "100vh",
          background:
            mode === "dark"
              ? "radial-gradient(1000px 600px at 20% -10%, rgba(30,215,96,0.15), transparent 60%), radial-gradient(900px 500px at 80% 10%, rgba(11,95,255,0.12), transparent 55%), #0b0f0e"
              : "radial-gradient(900px 500px at 15% -10%, rgba(11,95,255,0.12), transparent 60%), radial-gradient(900px 500px at 85% 10%, rgba(30,215,96,0.12), transparent 55%), #f6f9ff"
        }}
      >
        <Container maxWidth="xl" sx={{ py: 5 }}>
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              mb: 4
            }}
          >
            <Box>
              <Typography
                variant="h3"
                sx={{ fontWeight: 800, letterSpacing: 0.3 }}
              >
                Data Platform Metadata and Lineage
              </Typography>
              <Typography sx={{ mt: 1, color: "text.secondary" }}>
                ODP to FDP to CDP | Tables | Columns | Versions | Lineage
              </Typography>
            </Box>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <Button
                component={Link}
                to="/sql"
                variant="outlined"
                color="secondary"
              >
                SQL Generation
              </Button>
              <Button
                component={Link}
                to="/lineage/tables"
                variant="outlined"
                color="primary"
              >
                Table Lineage
              </Button>

               <Button
                  variant="contained"
                  onClick={() => setOpenIngest(true)}
                >
                  Upload Metadata
                </Button>

                <MetadataIngestDialog
                  open={openIngest}
                  onClose={() => setOpenIngest(false)}
                  onSuccess={() => setRefreshGraph(p => !p)}
                />

              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  gap: 1.5,
                  px: 2,
                  py: 1,
                  borderRadius: 999,
                  bgcolor: "background.paper",
                  border: "1px solid",
                  borderColor:
                    mode === "dark" ? "rgba(255,255,255,0.12)" : "rgba(15,23,42,0.12)",
                  boxShadow: mode === "dark" ? "0 8px 16px rgba(0,0,0,0.28)" : "0 3px 10px rgba(15,23,42,0.08)"
                }}
              >
                <Typography sx={{ fontWeight: 600 }}>
                  {mode === "dark" ? "Dark" : "Light"} Mode
                </Typography>
                <IconButton
                  onClick={() =>
                    setMode(prev => (prev === "dark" ? "light" : "dark"))
                  }
                  color="primary"
                >
                  {mode === "dark" ? <Brightness7 /> : <Brightness4 />}
                </IconButton>
              </Box>
            </Box>
          </Box>

          <Stack spacing={3}>
            <Box
              sx={{
                display: "grid",
                gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
                gap: 2
              }}
            >
              <MetricCard
                title="Summary"
                index={0}
                metrics={[
                  { label: "Total Layers", value: metrics.summary.layers },
                  { label: "Total Tables", value: metrics.summary.tables },
                  { label: "Total Versions", value: metrics.summary.versions },
                  { label: "Total Columns", value: metrics.summary.columns }
                ]}
              />

              <MetricCard
                title="ODP"
                index={1}
                metrics={[
                  { label: "Tables", value: odp.tables },
                  { label: "Versions", value: odp.versions },
                  { label: "Columns", value: odp.columns }
                ]}
              />

              <MetricCard
                title="FDP"
                index={2}
                metrics={[
                  { label: "Tables", value: fdp.tables },
                  { label: "Versions", value: fdp.versions },
                  { label: "Columns", value: fdp.columns }
                ]}
              />

              <MetricCard
                title="CDP"
                index={3}
                metrics={[
                  { label: "Tables", value: cdp.tables },
                  { label: "Versions", value: cdp.versions },
                  { label: "Columns", value: cdp.columns }
                ]}
              />
            </Box>

            <Paper
              elevation={0}
              sx={{
                p: 2,
                borderRadius: 2,
                bgcolor: "background.paper",
                border: "1px solid",
                borderColor: mode === "dark" ? "rgba(255,255,255,0.12)" : "rgba(15,23,42,0.12)",
                boxShadow: mode === "dark" ? "0 10px 24px rgba(0,0,0,0.35)" : "0 6px 18px rgba(15,23,42,0.08)",
                height: "75vh",
                maxHeight: "75vh",
                display: "flex",
                flexDirection: "column",
                overflow: "hidden",
                mt: 2
              }}
            >
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  mb: 1
                }}
              >
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  Neo4j Lineage Graph
                </Typography>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
                  <Box
                    sx={{
                      px: 1.5,
                      py: 0.5,
                      borderRadius: 999,
                      bgcolor:
                        mode === "dark"
                          ? "rgba(30,215,96,0.15)"
                          : "rgba(11,95,255,0.12)",
                      color: "primary.main",
                      fontWeight: 600,
                      fontSize: 12
                    }}
                  >
                    Live View
                  </Box>
                  <Button
                    variant="contained"
                    size="small"
                    startIcon={<Refresh />}
                    onClick={() => setRefreshGraph(p => !p)}
                  >
                    Refresh
                  </Button>
                </Box>
              </Box>

              <Divider sx={{ mb: 2 }} />

              <Box sx={{ flex: 1, minHeight: 0, height: "100%" }}>
                <LineageGraph refresh={refreshGraph} />
              </Box>
            </Paper>

            <Paper
              elevation={0}
              sx={{
                p: 2,
                borderRadius: 2,
                bgcolor: "background.paper",
                border: "1px solid",
                borderColor: mode === "dark" ? "rgba(255,255,255,0.12)" : "rgba(15,23,42,0.12)",
                boxShadow: mode === "dark" ? "0 10px 24px rgba(0,0,0,0.35)" : "0 6px 18px rgba(15,23,42,0.08)",
                height: "34vh",
                minHeight: 260,
                display: "flex",
                flexDirection: "column",
                overflow: "hidden"
              }}
            >
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  mb: 1
                }}
              >
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  Canvas Lineage Graph
                </Typography>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<Refresh />}
                  onClick={() => setRefreshGraph(p => !p)}
                >
                  Refresh
                </Button>
              </Box>

              <Divider sx={{ mb: 2 }} />

              <Box sx={{ flex: 1, minHeight: 0, height: "100%" }}>
                <LineageGraphPlaceholder refresh={refreshGraph} />
              </Box>
            </Paper>

          </Stack>
        </Container>
      </Box>
    </ThemeProvider>
  );
}
