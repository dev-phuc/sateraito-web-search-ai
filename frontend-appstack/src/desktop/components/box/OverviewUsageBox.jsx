import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

// Library UI imports
import { Card, Col, Form, OverlayTrigger, Row, Tooltip } from 'react-bootstrap';

// Hook components
import useTheme from '@/hooks/useTheme'

// Zustand
import useTenantConfigStore from '@/store/tenant_config';

// Constants

const LLMUsageBox = ({ data }) => {
  // Default hooks
  const { t } = useTranslation();

  // Zustand stores
  const { llmQuota } = useTenantConfigStore();

  // Use state

  // Handler

  if (!llmQuota) {
    return <></>;
  }

  const {
    quota: llm_quota_monthly,
    // llm_quota_remaining,
    used: llm_quota_used,
    last_reset: llm_quota_last_reset,
    next_reset: llm_quota_next_reset,
  } = llmQuota;

  // Return the component
  return (
    <>
      <div className="wrap-overview-usage">
        <div className="box p-3 bg-primary rounded mb-2">
          <div className="d-flex align-items-center justify-content-between">
            <h5>{t("LLM_QUOTA_MONTHLY")}</h5>
            <div>
              <div>
                <small className="ms-2">{llm_quota_last_reset ? `${t("LAST_RESET")}: ${new Date(llm_quota_last_reset).toLocaleDateString()}` : ''}</small>
              </div>
              <div>
                <small className="ms-2">{llm_quota_next_reset ? `${t("NEXT_RESET")}: ${new Date(llm_quota_next_reset).toLocaleDateString()}` : ''}</small>
              </div>
            </div>
          </div>
          <h3>{llm_quota_monthly || 0}</h3>
          <p>{t("LLM_QUOTA_MONTHLY_DESC")}</p>
        </div>
        <div className="box p-3 bg-success rounded mb-2">
          <h5>{t("LLM_QUOTA_REMAINING")}</h5>
          <h3>{llm_quota_monthly - llm_quota_used || 0}</h3>
          <p>{t("LLM_QUOTA_REMAINING_DESC")}</p>
        </div>
        <div className="box p-3 bg-danger rounded mb-2">
          <h5>{t("LLM_QUOTA_USED")}</h5>
          <h3>{llm_quota_used || 0}</h3>
          <p>{t("LLM_QUOTA_USED_DESC")}</p>
        </div>
      </div >
    </>
  );
};

export default LLMUsageBox;