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

  // Effects
  useEffect(() => {
    if (!isLoading) {
      getLLMConfiguration(tenant, app_id);
    }
  }, []);

  // Return component
  return (
    <>
      <Helmet>
        <title>{t("PAGE_TITLE_LLM_CONFIGURATION")}</title>
      </Helmet>

      <Container fluid className="p-0">
        <h1 className="h3 mb-3">{t("PAGE_TITLE_LLM_CONFIGURATION")}</h1>

        <Card>
          <Card.Body>
            {isLoading ? (
              <div className="text-center my-5">
                <Spinner animation="border" role="status">
                  <span className="visually-hidden">{t('TXT_LOADING')}</span>
                </Spinner>
              </div>
            ) : (
              <LLMConfigurationForm
                tenant={tenant}
                app_id={app_id}
                initialValues={llmConfiguration}
              />
            )}
          </Card.Body>
        </Card>
      </Container>
    </>
  );
};

export default LLMConfigurationAdminConsolePage;
