import React from "react";
import { createBrowserRouter } from "react-router";

// Providers
import AuthProvider from "@/provider/AuthProvider";

// Layouts
import LayoutAdmin from "@/layout/admin";

// Pages
import LoginPage from "@/pages/login";
import DashboardPage from "@/pages/admin/DashboardPage";
import DomainsManagement from "@/pages/admin/DomainsManagement";

// Higher-Order Component for protected routes
const ProtectedRoute = ({ element }) => {
  return <AuthProvider>{element}</AuthProvider>;
};

const router = createBrowserRouter([
  {
    path: ":tenant/:app_id/login",
    element: (
      <ProtectedRoute
        element={<LoginPage />}
      />
    ),
  },
  
  // Admin routes
  {
    path: ":tenant/:app_id/admin_console",
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
      {
        path: "domains",
        element: <DomainsManagement />,
      }
    ],
  },
]);

export default router;