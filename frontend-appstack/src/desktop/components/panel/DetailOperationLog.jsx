import { useRef, useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

// Library UI imports
import Markdown from 'react-markdown';
import { Card, Col, Form, Row } from 'react-bootstrap';

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

  // Return the component
  return (
    <>
      <Row>
        <Col md="6">
          <div className="mb-2">
            <strong>{t('TXT_APP_ID')}:</strong>
            {data?.app_id || ''}
          </div>
        </Col>
        <Col md="6">
          <div className="mb-2">
            <strong>{t('LABEL_DOMAIN')}:</strong>
            <a href={data?.client_domain || ''} target="_blank" rel="noopener noreferrer" className="ms-2">
              {data?.client_domain || ''}
            </a>
          </div>
        </Col>
        <Col md="6">
          <div className='mb-2'>
            <strong>{t('LABEL_STATUS')}:</strong>
            <span className={`ms-2 badge bg-${data?.status === 'completed' ? 'success' : data?.status === 'error' ? 'danger' : 'secondary'}`}>
              {data?.status || 'unknown'}
            </span>
          </div>
        </Col>
        <Col md="6">
          <div className="mb-2">
            <strong>{t('LABEL_CREATED_DATE')}:</strong>
            {data?.created_date || ''}
          </div>
        </Col>
        <Col md="12">
          {data?.error_message && (
            <div className="mb-2 text-error">
              <strong>{t('LABEL_ERROR_MESSAGE')}:</strong>
              {data?.error_message || ''}
            </div>
          )}
        </Col>
      </Row>


      <div className="mt-2">
        <strong>{t('LABEL_MODEL_NAME')}:</strong>
        <span className={`ms-2 badge bg-info`}>
          {data?.model_name || ''}
        </span>
      </div>
      <div className="mt-2">
        <strong>{t('LABEL_PROMPT')}:</strong>
      </div>
      <div className="" style={{ background: '#f8f9fa', padding: '8px', borderRadius: '4px' }}>
        <Markdown>{data?.prompt || ''}</Markdown>
      </div>
      <div className="mt-2">
        <strong>{t('LABEL_RESPONSE')}:</strong>
      </div>
      <div className="react-markdown-style" style={{ background: '#f8f9fa', padding: '8px', borderRadius: '4px' }}>
        <Markdown>{responseText}</Markdown>
      </div>

      {/* Metadata section */}
      {data?.metadata && (
        <div className="mt-4">
          <h5>{t('LABEL_RESOURCE')}</h5>
          {/* Search Results */}
          {Array.isArray(metadata.search_results) && metadata.search_results.length > 0 && (
            <div className="mb-3">
              <ul>
                {metadata.search_results.map((item, idx) => (
                  <li key={idx}>
                    <div className='d-flex justify-content-between'>
                      <div>
                        <a href={item.url} target="_blank" rel="noopener noreferrer">{item.title}</a>
                      </div>
                      {item.last_updated && (
                        <div>
                          <strong>{t('LABEL_UPDATED_DATE')}:</strong>
                          {item.last_updated}
                        </div>
                      )}
                    </div>
                    <div><strong></strong> <Markdown>{item.snippet}</Markdown></div>
                    <hr />
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </>
  );
};

export default DetailOperationLogPanel;