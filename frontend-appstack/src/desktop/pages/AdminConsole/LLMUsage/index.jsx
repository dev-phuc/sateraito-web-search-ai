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
const LLMUsageAdminConsolePage = () => {
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
        <title>{t("PAGE_TITLE_LLM_USAGE_MANAGER")}</title>
      </Helmet>

      <Container fluid className="p-0">
        <h1>
          LLM Usage - Admin console
        </h1>
      </Container>

    </>
  );
};

export default LLMUsageAdminConsolePage;
