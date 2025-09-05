import React from "react";
import { lazy } from "@loadable/component";

// Layouts
import AdminConsoleLayout from "@/desktop/layouts/AdminConsole";

const Page404 = lazy(() => import("@/desktop/pages/Page404"));

// Auth
const SignIn = lazy(() => import("@/desktop/pages/auth/SignIn"));

// Admin console
const DashboardAdminConsolePage = lazy(() => import("@/desktop/pages/AdminConsole/Dashboard"));
const ClientWebsitesAdminConsolePage = lazy(() => import("@/desktop/pages/AdminConsole/ClientWebsites"));

let routes = [
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
