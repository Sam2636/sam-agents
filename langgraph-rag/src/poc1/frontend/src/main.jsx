import { ChakraProvider } from "@chakra-ui/react";
import App from "./App.jsx";
import { createRoot } from "react-dom/client";

createRoot(document.getElementById("root")).render(
  <ChakraProvider>
    <App />
  </ChakraProvider>
);
