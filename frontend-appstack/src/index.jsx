import React from "react";
import { BrowserRouter, useLocation } from "react-router-dom";
import { createRoot } from "react-dom/client";

import App from "@/App";

import "sweetalert2/src/sweetalert2.scss";
import '@/assets/scss/sateraito_style.scss';

const container = document.getElementById("root");
const root = createRoot(container);
root.render(
  <BrowserRouter>
    <App />
  </BrowserRouter>
);