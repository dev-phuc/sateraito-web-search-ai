import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import moment from 'moment';

// Library UI imports
import { Card, Col, Form, OverlayTrigger, Row, Tooltip, ProgressBar } from 'react-bootstrap';

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

  // Calculate usage percentage
  const usagePercentage = llmQuota?.quota ? Math.round((llmQuota.used / llmQuota.quota) * 100) : 0;
  const remainingPercentage = 100 - usagePercentage;

  // Return the component
  return (
    <>
      <div className="wrap-overview-usage-new">
        <Card className="usage-unified-card">
          <Card.Body >
            {/* Header */}
            <div className="d-flex align-items-center justify-content-between ">
              <div>
                <h4 className="mb-0 fw-bold text-dark">{t("USAGE_OVERVIEW")}</h4>
              </div>
              <div className=" text-center reset-info">
                {/* <small className="text-muted">
                  {llmQuota?.last_reset && `${t("LAST_RESET")}: ${llmQuota.last_reset}`}
                </small> */}
                <span className='mdi mdi-autorenew'></span>
                <small >
                  {llmQuota?.next_reset && `${t("NEXT_RESET")}: ${llmQuota.next_reset}`}
                </small>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="usage-progress-section">
              <div className="d-flex justify-content-between align-items-center mb-1">
                {/* <span className="small text-muted">Progress</span>
                <div className="d-flex align-items-center">
                  <span className="text-danger  small">{llmQuota?.used || 0}</span>
                  <span className="text-success small">/{llmQuota?.quota || 0}</span>
                </div> */}
              </div>
              <div className="usage-progress-bar">
                <div className="progress-track">
                  <div 
                    className="progress-fill used" 
                    style={{width: `${usagePercentage}%`}}
                  ></div>
                  <div 
                    className="progress-fill remaining" 
                    style={{width: `${remainingPercentage}%`}}
                  ></div>
                </div>
              </div>
            </div>

            {/* Stats Row */}
            <Row className='mt-3'>
              <Col md={4}>
                <div className="stat-item">
                  <div className="usage-stat">
                    <div className="stat-icon-small quota-icon me-2">
                      <i className="mdi mdi-chart-timeline-variant"></i>
                    </div>
                    <div className="stat-value-small">{llmQuota?.quota || 0}</div>

                    <span className="stat-label-small">{t("LLM_QUOTA_MONTHLY")}</span>
                  </div>
                </div>
              </Col>
              <Col md={4}>
                <div className="stat-item">
                  <div className="usage-stat">
                    <div className="stat-icon-small used-icon me-2">
                      <i className="mdi mdi-chart-donut"></i>
                    </div>
                    <div className="stat-value-small">{llmQuota?.used || 0}</div>
                    <span className="stat-label-small">{t("LLM_QUOTA_USED")}</span>
                  </div>
                </div>
              </Col>
              <Col md={4}>
                <div className="stat-item">
                  <div className="usage-stat">
                    <div className="stat-icon-small remaining-icon me-2">
                      <i className="mdi mdi-battery-60"></i>
                    </div>
                    <div className="stat-value-small">{llmQuota?.remaining || 0}</div>
                    <span className="stat-label-small">{t("LLM_QUOTA_REMAINING")}</span>
                  </div>
                </div>
              </Col>
            </Row>

            {/* Footer */}

            {loading && <MakerLoading />}
          </Card.Body>
        </Card>
      </div>
    </>
  );
};

export default LLMUsageBox;