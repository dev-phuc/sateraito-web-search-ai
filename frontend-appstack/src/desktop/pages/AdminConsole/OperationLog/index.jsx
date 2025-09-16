// Framework import
import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Helmet } from "react-helmet-async";
import { useNavigate, useParams } from 'react-router-dom';

// Components 
import { Modal } from "react-bootstrap";

// Zustand

// Hook components
import useTheme from "@/hooks/useTheme";

// Context components

// Library imports
// Library IU imports
import { Container } from "react-bootstrap";

// Constant value

// Components
import OperationLogsTable from "@/desktop/components/table/OperationLog";

// Define the component
const OperationLogAdminConsolePage = () => {
  // Default hooks
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { tenant, app_id } = useParams();

  // Zustand stores

  // Use hooks state
  const { showNotice } = useTheme();

  // state

  // Handler method

  // Effects
  useEffect(() => {
  }, []);

  // Return component
  return (
    <>
      <Helmet>
        <title>{t("PAGE_TITLE_OPERATION_LOGS")}</title>
      </Helmet>

      <Container fluid className="p-0">
        {/* Table Operation Logs */}
        <OperationLogsTable
          tenant={tenant}
          app_id={app_id}
        />
      </Container>
    </>
  );
};

export default OperationLogAdminConsolePage;
