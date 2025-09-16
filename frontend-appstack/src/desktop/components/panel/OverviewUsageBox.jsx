import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

// Library UI imports
import { Card, Col, Form, Row } from 'react-bootstrap';

// Hook components
import useTheme from '@/hooks/useTheme'

// Zustand
import useStoreLLMUsage from '@/store/llm_usage';

// Constants

const OverviewUsageBoxPanel = ({ data }) => {
  // Default hooks
  const { t } = useTranslation();

  // Zustand stores
  const { llmUsage } = useStoreLLMUsage();

  // Use state

  // Handler

  if (!llmUsage) {
    return <></>;
  }

  const {
    llm_quota_monthly,
    llm_quota_remaining,
    llm_quota_used,
    llm_quota_last_reset,
  } = llmUsage;

  // Return the component
  return (
    <>
      <div className="wrap-overview-usage d-flex justify-content-between mb-4">
        <div className="box p-3 bg-primary rounded" style={{ width: '32%' }}>
          <div className="d-flex align-items-center justify-content-between">
            <h5>{t("LLM_QUOTA_MONTHLY")}</h5>
            <small className="ms-2">{llm_quota_last_reset ? `${t("LAST_RESET")}: ${new Date(llm_quota_last_reset).toLocaleDateString()}` : ''}</small>
          </div>
          <h3>{llm_quota_monthly || 0}</h3>
          <p>{t("LLM_QUOTA_MONTHLY_DESC")}</p>
        </div>
        <div className="box p-3 bg-success rounded" style={{ width: '32%' }}>
          <h5>{t("LLM_QUOTA_REMAINING")}</h5>
          <h3>{llm_quota_remaining || 0}</h3>
          <p>{t("LLM_QUOTA_REMAINING_DESC")}</p>
        </div>
        <div className="box p-3 bg-danger rounded" style={{ width: '32%' }}>
          <h5>{t("LLM_QUOTA_USED")}</h5>
          <h3>{llm_quota_used || 0}</h3>
          <p>{t("LLM_QUOTA_USED_DESC")}</p>
        </div>
      </div>
    </>
  );
};

export default OverviewUsageBoxPanel;