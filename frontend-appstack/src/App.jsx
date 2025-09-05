import React, { Suspense, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useRoutes } from "react-router-dom";
// import { Provider } from "react-redux";
import { HelmetProvider, Helmet } from "react-helmet-async";

// I18n
import '@/locales'
import routes from "@/routes";

import ThemeProvider from "@/contexts/ThemeProvider";
import SidebarProvider from "@/contexts/SidebarProvider";
import LayoutProvider from "@/contexts/LayoutProvider";
import AuthProvider from "@/contexts/JWTProvider";
import UserConfigProvider from "@/contexts/UserConfigProvider";

import ChartJsDefaults from "@/utils/ChartJsDefaults";

// define a new console
if (import.meta.env.MODE === "production") {
  console.log = () => { };
  console.info = () => { };
  console.warn = () => { };
  console.error = () => { };
  console.table = () => { };
} else {
}

const App = () => {
  const { t } = useTranslation();
  const content = useRoutes(routes);

  return (
    // create context and prevent memory leaks
    <HelmetProvider>

      {/* SEO head */}
      <Helmet
        titleTemplate={"%s | " + t("TXT_APP_NAME")}
        defaultTitle={t("TXT_APP_NAME")}
      />

      <ThemeProvider>
        <SidebarProvider>
          {/* use Sidebar and useLayout */}
          <LayoutProvider>
            <ChartJsDefaults />

            {/* permission auth */}
            <AuthProvider>
              <UserConfigProvider>
                {content}
              </UserConfigProvider>
            </AuthProvider>

          </LayoutProvider>
        </SidebarProvider>
      </ThemeProvider>

    </HelmetProvider>
  );
};

export default App;
