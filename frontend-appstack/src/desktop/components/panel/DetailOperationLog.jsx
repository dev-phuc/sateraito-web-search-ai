import { useRef, useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

// Library UI imports
import Markdown from 'react-markdown';
import { Card, Col, Form, Row, Badge, Alert } from 'react-bootstrap';

// Hook components
import useTheme from '@/hooks/useTheme'

// Zustand

// Constants

const DetailOperationLogPanel = ({ data }) => {
  // Default hooks
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { showNotice } = useTheme();

  // Zustand stores

  // Use state

  // Handler

  useEffect(() => {
    console.log(data);
  }, [data]);

  // Parse metadata if available
  let metadata = {};
  try {
    metadata = data?.metadata ? JSON.parse(data.metadata) : {};
  } catch (e) {
    metadata = {};
  }

  let responseText = data?.response || '';
  const search_results = Array.isArray(metadata.search_results) ? metadata.search_results : [];
  search_results.forEach((item, index) => {
    const linkMarkdown = `[[${index + 1}]](${item.url})`;
    responseText = responseText.replaceAll(`[${index + 1}]`, linkMarkdown);
  });

  // Get status color and icon
  const getStatusConfig = (status) => {
    switch(status) {
      case 'completed':
        return { 
          color: 'success', 
          icon: 'mdi mdi-check-circle-outline',
          text: status,
          bg: 'rgba(25, 135, 84, 0.1)'
        };
      case 'error':
        return { 
          color: 'danger', 
          icon: 'mdi mdi-alert-circle-outline',
          text: status,
          bg: 'rgba(41, 39, 39, 0.1)'
        };
      case 'pending':
        return { 
          color: 'warning', 
          icon: 'mdi mdi-timer-sand',
          text: status,
          bg: 'rgba(255, 193, 7, 0.1)'
        };
      default:
        return { 
          color: 'secondary', 
          icon: 'mdi mdi-help-circle-outline',
          text: status || 'unknown',
          bg: 'rgba(108, 117, 125, 0.1)'
        };
    }
  };

  const statusConfig = getStatusConfig(data?.status);

  // Return the component
  return (
    <div className="operation-log-detail" style={{ maxHeight: '80vh', overflowY: 'auto' }}>
      {/* Header Section with Status */}
      <Card className="mb-0 border-0 shadow-sm">
        <Card.Body className="pb-2">

          {/* Error Message Alert */}
          {data?.error_message && (
            <Alert variant="danger" className="mb-2 py-2 border-0" style={{ backgroundColor: 'rgba(220, 53, 69, 0.05)' }}>
              <div className="d-flex align-items-start">
                <i className="fas fa-exclamation-triangle me-2 mt-1"></i>
                <div style={{ fontSize: '0.9rem' }}>
                  <strong>Error:</strong> {data?.error_message}
                </div>
              </div>
            </Alert>
          )}

          {/* Compact Info Row */}
          <div className="d-flex flex-wrap gap-2 align-items-center">
            <div className="d-flex align-items-center ">
              <i className="fas fa-code me-1 text-primary"></i>
              <span className="text-muted me-1" style={{ fontSize: '0.9rem' }}>{t('TXT_APP_ID')}</span>
              <code className="text-primary" style={{ fontSize: '0.9rem' }}>{data?.app_id || 'N/A'}</code>
            </div>
            
            <div className="d-flex align-items-center  px-2 py-1 rounded-2 ">
              <i className="fas fa-globe me-1 text-success"></i>
              <a 
                href={data?.client_domain || ''} 
                target="_blank" 
                rel="noopener noreferrer" 
                className="text-decoration-none text-success"
                style={{ fontSize: '0.9rem' }}
                title={data?.client_domain}
              >
                <span className="text-muted me-1" style={{ fontSize: '0.9rem' }}>{t('LABEL_DOMAIN')}</span>

                {data?.client_domain ? data.client_domain.replace(/^https?:\/\//, '').substring(0, 50) + (data.client_domain.length > 50 ? '...' : '') : 'N/A'}
                <i className="fas fa-external-link-alt ms-1"></i>
              </a>
            </div>
            <div className="text-muted small">
              <i className="fas fa-clock me-1"></i>
              {data?.created_date || ''}
            </div>

          </div>
        </Card.Body>
      </Card>

      {/* Prompt Section */}
      <Card className="mb-3 border-0 shadow-sm">
        <Card.Body className="pb-2">
          <div className="d-flex align-items-center mb-2 gap-2">
            <h4 className="mb-0 fw-bold me-2" style={{ color: '#6b46c1' }}>{t('LABEL_PROMPT')}</h4>
            <div className="d-flex align-items-center ">
              {/* <span className="text-muted me-1" style={{ fontSize: '0.9rem' }}>{t('LABEL_MODEL_NAME')}:</span> */}
              <span className="badge ai-model px-2 py-1  small chip">
                <i className="mdi mdi-robot "></i>
                {data?.model_name}
              </span>
            </div>
            <div>
              <Badge bg={statusConfig.color} className="small chip">
                <i className={statusConfig.icon}></i>
                {statusConfig.text.toUpperCase()}
              </Badge>
            </div>
          </div>
          <div 
            className="content-box p-2 rounded-3 position-relative"
            style={{ 
              background: 'linear-gradient(135deg, #fef3ff 0%, #f0f0ff 50%, #e6f3ff 100%)', 
              minHeight: '50px',
              boxShadow: '0 1px 3px rgba(139, 92, 246, 0.1)'
            }}
          >
            <div className="markdown-content" style={{ fontSize: '0.9rem' }}>
              <Markdown>{data?.prompt || 'No prompt available'}</Markdown>
            </div>
          </div>
        </Card.Body>
      </Card>

      {/* Response Section */}
      <Card className="mb-3 border-0 shadow-sm">
        <Card.Body className="pb-2">
          <div className="d-flex align-items-center mb-2">
            <h4 className="mb-0 fw-bold" style={{ color: '#0f766e' }}>{t('LABEL_RESPONSE')}</h4>
          </div>
          <div 
            className="content-box p-2 rounded-3 position-relative"
            style={{ 
              background: 'linear-gradient(135deg, #f0fdfa 0%, #e6fffa 50%, #f0f9ff 100%)', 
              minHeight: '60px',
              boxShadow: '0 1px 3px rgba(20, 184, 166, 0.1)'
            }}
          >
            <div className="react-markdown-style" style={{ fontSize: '0.9rem' }}>
              <Markdown>{responseText || 'No response available'}</Markdown>
            </div>
          </div>
        </Card.Body>
      </Card>

      {/* Resources/Metadata Section */}
      {data?.metadata && Array.isArray(metadata.search_results) && metadata.search_results.length > 0 && (
        <Card className="border-0 shadow-sm">
          <Card.Body className="pb-2">
            <div className="d-flex align-items-center mb-2">
              <i className="fas fa-link me-2 text-primary"></i>
              <h6 className="mb-0 fw-bold text-dark">{t('LABEL_RESOURCE')}</h6>
              <Badge bg="light" text="dark" className="ms-2">
                {metadata.search_results.length}
              </Badge>
            </div>
            
            <div className="resources-list">
              {metadata.search_results.map((item, idx) => (
                <div 
                  key={idx} 
                  className="resource-item p-2 mb-2  position-relative"
                  // onMouseEnter={(e) => {
                  //   e.target.style.backgroundColor = '#f1f5f9';
                  // }}
                  // onMouseLeave={(e) => {
                  //   e.target.style.backgroundColor = '#fafbfc';
                  // }}
                >
                  <div className="d-flex justify-content-between align-items-start mb-1">
                    <a 
                      href={item.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="fw-medium text-decoration-none text-primary"
                      style={{ fontSize: '0.9rem' }}
                      title={item.title}
                    >
                      <i className="fas fa-external-link-alt me-1"></i>
                      {item.title ? (item.title.length > 60 ? item.title.substring(0, 60) + '...' : item.title) : 'Untitled Resource'}
                    </a>
                    {item.last_updated && (
                      <Badge bg="light" text="muted" style={{ fontSize: '0.75rem' }}>
                        <i className="far fa-clock me-1"></i>
                        {item.last_updated}
                      </Badge>
                    )}
                  </div>
                  {item.snippet && (
                    <p className="mb-0 text-muted lh-sm" style={{ fontSize: '0.85rem' }}>
                      {item.snippet}
                    </p>
                  )}

                </div>
              ))}
            </div>
          </Card.Body>
        </Card>
      )}


    </div>
  );
};

export default DetailOperationLogPanel;