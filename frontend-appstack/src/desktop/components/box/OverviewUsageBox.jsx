import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import moment from 'moment';

// Library UI imports
import { Card, Col, Form, OverlayTrigger, Row, Tooltip } from 'react-bootstrap';

// Hook components
import useTheme from '@/hooks/useTheme'

// Zustand
import useTenantConfigStore from '@/store/tenant_config';

// Constants

// Components
import MakerLoading from '../MakerLoading';

const LLMUsageBox = ({ data }) => {
  // Default hooks
  const { t } = useTranslation();

  // Zustand stores
  const { loading, llmQuota } = useTenantConfigStore();

  // Use state

  // Handler

  // Return the component
  return (
    <>
      <div className="wrap-overview-usage">
        <div className="box p-3 bg-primary rounded mb-2 pos-relative">
          <div className="d-flex align-items-center justify-content-between">
            <h5>{t("LLM_QUOTA_MONTHLY")}</h5>
            <div>
              <div>
                <small className="ms-2">
                  {llmQuota?.last_reset && (
                    `${t("LAST_RESET")}: ${llmQuota.last_reset}`
                  )}
                </small>
              </div>
              <div>
                <small className="ms-2">
                  {llmQuota?.next_reset && (
                    `${t("NEXT_RESET")}: ${llmQuota.next_reset}`
                  )}
                </small>
              </div>
            </div>
          </div>
          <h3>{llmQuota?.quota || 0}</h3>
          <p>{t("LLM_QUOTA_MONTHLY_DESC")}</p>

          {loading && <MakerLoading />}
        </div>

        <div className="box p-3 bg-success rounded mb-2 pos-relative">
          <h5>{t("LLM_QUOTA_REMAINING")}</h5>
          <h3>{llmQuota?.remaining || 0}</h3>
          <p>{t("LLM_QUOTA_REMAINING_DESC")}</p>

          {loading && <MakerLoading />}
        </div>

        <div className="box p-3 bg-danger rounded mb-2 pos-relative">
          <h5>{t("LLM_QUOTA_USED")}</h5>
          <h3>{llmQuota?.used || 0}</h3>
          <p>{t("LLM_QUOTA_USED_DESC")}</p>

          {loading && <MakerLoading />}
        </div>
      </div >
    </>
  );
};

export default LLMUsageBox;