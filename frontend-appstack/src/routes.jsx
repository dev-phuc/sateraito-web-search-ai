import React from "react";
import { lazy } from "@loadable/component";

// Layouts
import AuthLayout from "@/desktop/layouts/Auth";
import AdminConsoleLayout from "@/desktop/layouts/AdminConsole";

const Page404 = lazy(() => import("@/desktop/pages/Page404"));

// Auth
const SignIn = lazy(() => import("@/desktop/pages/auth/SignIn"));

// Admin console
const DashboardAdminConsolePage = lazy(() => import("@/desktop/pages/AdminConsole/Dashboard"));
const ClientWebsitesAdminConsolePage = lazy(() => import("@/desktop/pages/AdminConsole/ClientWebsites"));
const BoxSearchConfigAdminConsolePage = lazy(() => import("@/desktop/pages/AdminConsole/BoxSearchConfig"));
const LLMConfigurationAdminConsolePage = lazy(() => import("@/desktop/pages/AdminConsole/LLMConfiguration"));
const OperationLogAdminConsolePage = lazy(() => import("@/desktop/pages/AdminConsole/OperationLog"));

// Box search
const BoxSearchPage = lazy(() => import("@/desktop/pages/BoxSearch"));

let routes = [
  // Auth
  {
    path: "/:tenant/:app_id/auth",
    element: <AuthLayout />,
    children: [
      {
        path: "login",
        element: <SignIn />,
      },
    ],
  },

  // "admin_console"
  {
    // Example "/vn2.sateraito.co.jp/default/admin_console"
    // path: "/admin_console",
    path: "/:tenant/:app_id/admin_console",
    element: <AdminConsoleLayout />,
    children: [
      {
        path: "dashboard",
        element: <DashboardAdminConsolePage />,
      },
      {
        path: "domains",
        element: <ClientWebsitesAdminConsolePage />,
      },
      {
        path: "box-search-config",
        element: <BoxSearchConfigAdminConsolePage />,
      },
      {
        path: "ai-configuration",
        element: <LLMConfigurationAdminConsolePage />,
      },
      {
        path: "logs",
        element: <OperationLogAdminConsolePage />,
      },
      // {
      //   path: "userinfo",
      //   element: <UserInfoAdminConsolePage />,
      // },
      // {
      //   path: "account",
      //   element: <AccountAdminConsolePage />,
      // },
      // {
      //   path: "type-book",
      //   element: <TypeBookAdminConsolePage />,
      // },
      // // {
      // //   path: "category-book",
      // //   element: <CategoryBookAdminConsolePage />,
      // // },
      // {
      //   path: "book",
      //   element: <BookAdminConsolePage />,
      // },
      // {
      //   path: "setting",
      //   element: <SettingAdminConsolePage />,
      // },
    ],
  },

  // "box_search"
  {
    path: "/:tenant/:app_id/box_search",
    element: <BoxSearchPage />,
  },

  // "*"
  {
    path: "*",
    children: [
      {
        path: "*",
        element: <Page404 />,
      },
    ],
  },
];

export default routes;
