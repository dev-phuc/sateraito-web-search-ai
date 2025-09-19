// Framework import
import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Helmet } from "react-helmet-async";
import { useNavigate, useParams } from 'react-router-dom';

// Components 
import { Container, Card, Spinner } from "react-bootstrap";

// Zustand
import useStoreLLMConfiguration from '@/store/llm_configuration';

// Hook components
import useTheme from "@/hooks/useTheme";

// Context components

// Library imports

// Constant value

// Components
import LLMConfigurationForm from '@/desktop/components/form/LLMConfiguration';

// Define the component
const LLMConfigurationAdminConsolePage = () => {
  // Default hooks
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { tenant, app_id } = useParams();

  // Zustand stores
  const { isLoading, llmConfiguration, getLLMConfiguration } = useStoreLLMConfiguration();

  // Use hooks state
  const { showNotice } = useTheme();

  // state

  // Handler method
  const handlerLoadData = async () => {
    const { success, message } = await getLLMConfiguration(tenant, app_id);
    if (!success) {
      showNotice("danger", t(message));
    }
  };

  const handlerAfterSubmit = (data) => {
    handlerLoadData();
  };

  // Effects
  useEffect(() => {
    if (!isLoading) {
      handlerLoadData();
    }
  }, []);

  // Return component
  return (
    <>
      <Helmet>
        <title>{t("PAGE_TITLE_LLM_CONFIGURATION")}</title>
      </Helmet>

      <Container fluid className="p-0">
        <LLMConfigurationForm
          tenant={tenant}
          app_id={app_id}
          initialValues={llmConfiguration}
          afterSubmit={handlerAfterSubmit}
        />
      </Container>
    </>
  );
};

export default LLMConfigurationAdminConsolePage;
