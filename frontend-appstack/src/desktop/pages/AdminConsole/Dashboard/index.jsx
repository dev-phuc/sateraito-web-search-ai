// Framework import
import React, { useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Helmet } from "react-helmet-async";

// Redux components

// Hook components
import useTheme from "@/hooks/useTheme";

// Context components

// Library imports
// Library IU imports
import { Container } from "react-bootstrap";

// Constant value

// Components

// Define the component
const DashboardAdminConsolePage = () => {
  // Use default
  const { t } = useTranslation();

  // Use hooks state

  // state

  useEffect(() => {
  }, []);

  // Return component
  return (
    <React.Fragment>
      <Helmet>
        <title>{t("PAGE_TITLE_DASHBOARD_MANAGER")}</title>
      </Helmet>

      <Container fluid className="p-0">
        <h1>Dashboard - Admin console</h1>
      </Container>

    </React.Fragment>
  );
};

export default DashboardAdminConsolePage;
