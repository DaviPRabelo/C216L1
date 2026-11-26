import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import { ProvedorDeSessao } from "./context/SessaoContext.jsx";
import "./index.css";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <ProvedorDeSessao>
      <App />
    </ProvedorDeSessao>
  </StrictMode>,
);
