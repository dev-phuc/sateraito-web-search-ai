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
    <>
      <Helmet>
        <title>{t("PAGE_TITLE_DASHBOARD_MANAGER")}</title>
      </Helmet>

      <Container fluid className="p-0">
        <div className="w-100 h-100 d-flex justify-content-center align-items-center bg-light">
          <div variant="info" className="bg-white rounded p-4 text-center">
            <h3>
              The Dashboard feature is coming soon!
            </h3>
            <p>
              We are working hard to bring you this feature. Stay tuned for updates.
            </p>
          </div>
        </div>
      </Container>

    </>
  );
};

export default DashboardAdminConsolePage;
