import React from "react";
import { createBrowserRouter } from "react-router";

// Providers
import AuthProvider from "@/provider/AuthProvider";

// Layouts
import LayoutAdmin from "@/layout/admin";

// Pages
import LoginPage from "@/pages/login";
import LandingPage from "@/pages/landing/LandingPage";
import DashboardPage from "@/pages/admin/DashboardPage";

// Higher-Order Component for protected routes
const ProtectedRoute = ({ element }) => {
  return <AuthProvider>{element}</AuthProvider>;
};

const router = createBrowserRouter([
  {
    path: "/",
    element: <LandingPage />,
  },
  {
    path: "/dang-nhap",
    element: (
      <ProtectedRoute
        element={<LoginPage />}
      />
    ),
  },
  
  // Admin routes
  {
    path: "/admin_console",
    element: (
      <ProtectedRoute
        element={<LayoutAdmin />}
      />
    ),
    children: [
      {
        index: true,
        element: <DashboardPage />,
      },
    ],
  },
]);

export default router;