// Framework import
import React, { useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Helmet } from "react-helmet-async";
import { useParams } from "react-router-dom";

// Zustand store
import useTenantConfigStore from "@/store/tenant_config";

// Hook components
import useTheme from "@/hooks/useTheme";

// Context components

// Library imports
// Library IU imports
import { Container } from "react-bootstrap";

// Constant value

// Components
import TenantInformationBox from "@/desktop/components/box/TenantInformation";
import ContractInformationBox from "@/desktop/components/box/ContractInformation";
import LLMConfigurationBox from "@/desktop/components/box/LLMConfiguration";
import LLMUsageBox from "@/desktop/components/box/OverviewUsageBox";
import LLMUsageStatisticsBox from "@/desktop/components/box/LLMUsageStatistics";
import LLMClientWebsiteUsageStatisticsBox from "@/desktop/components/box/LLMClientWebsiteUsagePerMonth";
import OperationLogBox from "@/desktop/components/box/OperationLogBox";

// Define the component
const DashboardAdminConsolePage = () => {
  // Use default
  const { tenant, app_id } = useParams();
  const { t } = useTranslation();

  // Zustand store
  const { loaded, loading, error, fetchTenantConfig } = useTenantConfigStore();

  // Use hooks state

  // state

  useEffect(() => {
    if (!loading && !loaded && !error) {
      fetchTenantConfig(tenant, app_id);
    }
  }, []);

  // Return component
  return (
    <>
      <Helmet>
        <title>{t("PAGE_TITLE_DASHBOARD_MANAGER")}</title>
      </Helmet>

      <Container fluid className="p-0">
        {/* Grid flexible layout - 3 columns */}
        <div className="row g-3">
          <div className="col-4">
            <div className="wrap-box-dashboard circle-bg mb-3">
              <TenantInformationBox />
            </div>

            <div className="wrap-box-dashboard circle-bg mb-3">
              <ContractInformationBox />
            </div>

            <div className="wrap-box-dashboard circle-bg mb-3">
              <LLMConfigurationBox />
            </div>
          </div>

          <div className="col-4">
            <div className="wrap-box-dashboard mb-3">
              <LLMUsageStatisticsBox />
            </div>

            <div className="wrap-box-dashboard mb-3">
              <LLMClientWebsiteUsageStatisticsBox />
            </div>
          </div>

          <div className="col-4">
            <div className="mb-3">
              <LLMUsageBox />
            </div>

            <div className="wrap-box-dashboard mb-3">
              <OperationLogBox />
            </div>
          </div>
        </div>

      </Container>
    </>
  );
};

export default DashboardAdminConsolePage;
