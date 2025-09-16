// Framework import
import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Helmet } from "react-helmet-async";
import { useNavigate, useParams } from 'react-router-dom';

// Components 
import { Container, Modal } from "react-bootstrap";

// Zustand
import useStoreBoxSearchConfig from '@/store/box_search_config';

// Hook components
import useTheme from "@/hooks/useTheme";

// Context components

// Library imports

// Constant value

// Components
import BoxSearchConfigForm from '@/desktop/components/form/BoxSearchConfig';
import BoxSearchConfigPreview from '@/desktop/components/panel/BoxSearchConfigPreview';

// Define the component
const BoxSearchConfigAdminConsolePage = () => {
  // Default hooks
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { tenant, app_id } = useParams();

  // Zustand stores
  const { isLoading, boxSearchConfig, getBoxSearchConfig } = useStoreBoxSearchConfig();

  // Use hooks state
  const { showNotice } = useTheme();

  // state

  // Handler method

  // Effects
  useEffect(() => {
    if (!isLoading) {
      getBoxSearchConfig(tenant, app_id);
    }
  }, []);

  // Return component
  return (
    <>
      <Helmet>
        <title>{t("PAGE_TITLE_BOX_SEARCH_CONFIG")}</title>
      </Helmet>

      <Container fluid className="p-0">
        <div className="d-flex flex-row h-100">
          {/* Form config - Left */}
          <div className="flex-grow-1 h-100 overflow-auto" style={{
            maxWidth: "600px",
          }}
          >
            <BoxSearchConfigForm
              tenant={tenant}
              app_id={app_id}
              data={boxSearchConfig}
              afterSubmit={() => {
                getBoxSearchConfig(tenant, app_id);
              }}
            />
          </div>

          {/* Panel preview - Right */}
          <div className="flex-grow-1 p-3 border-start" style={{ background: "#fafbfc" }}>
            <BoxSearchConfigPreview
              tenant={tenant}
              app_id={app_id}
              data={boxSearchConfig}
            />
          </div>
        </div>
      </Container>
    </>
  );
};

export default BoxSearchConfigAdminConsolePage;
