import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Form, Button, Row, Col, Card } from "react-bootstrap";
import useTheme from '@/hooks/useTheme';
import { validateDomainOrUrl } from '@/utils';

const DomainFilter = ({ values, handleChange, setFieldValue }) => {
  const { t } = useTranslation();
  const { showNotice } = useTheme();
  
  const [currentSearchDomain, setCurrentSearchDomain] = useState('');
  const [currentExcludedDomain, setCurrentExcludedDomain] = useState('');

  // Domain array handlers
  const addSearchDomain = (setFieldValue, values) => {
    const trimmedDomain = currentSearchDomain.trim().toLowerCase();
    if (trimmedDomain) {
      if (!validateDomainOrUrl(trimmedDomain)) {
        showNotice('error', t('MSG_ERROR_DOMAIN_INVALID'));
        return;
      }
      const currentDomains = values.search_domain_filter || [];
      if (currentDomains.includes(trimmedDomain)) {
        showNotice('warning', t('MSG_WARNING_DOMAIN_ALREADY_EXISTS'));
        return;
      }
      setFieldValue('search_domain_filter', [...currentDomains, trimmedDomain]);
      setCurrentSearchDomain('');
    }
  };

  const removeSearchDomain = (setFieldValue, values, indexToRemove) => {
    const currentDomains = values.search_domain_filter || [];
    setFieldValue('search_domain_filter', currentDomains.filter((_, index) => index !== indexToRemove));
  };

  const addExcludedDomain = (setFieldValue, values) => {
    const trimmedDomain = currentExcludedDomain.trim().toLowerCase();
    if (trimmedDomain) {
      if (!validateDomainOrUrl(trimmedDomain)) {
        showNotice('error', t('MSG_ERROR_DOMAIN_INVALID'));
        return;
      }
      const currentDomains = values.excluded_domain_filter || [];
      if (currentDomains.includes(trimmedDomain)) {
        showNotice('warning', t('MSG_WARNING_DOMAIN_ALREADY_EXISTS'));
        return;
      }
      setFieldValue('excluded_domain_filter', [...currentDomains, trimmedDomain]);
      setCurrentExcludedDomain('');
    }
  };

  const removeExcludedDomain = (setFieldValue, values, indexToRemove) => {
    const currentDomains = values.excluded_domain_filter || [];
    setFieldValue('excluded_domain_filter', currentDomains.filter((_, index) => index !== indexToRemove));
  };

  return (
		<Card md={12} className="mb-4 shadow-sm domain-filter-container">
      {/* Domain Filter Header */}
      <div className="border-0 mb-3">
        <div >
          <div className="d-flex align-items-center justify-content-between mb-3">
            <div className="d-flex align-items-center">
              <div>
								<div className="fw-bold text-base mb-1 d-flex align-items-center">
									<i className="mdi mdi-filter  " style={{ fontSize: '18px' }}></i>

									{t('LABEL_DOMAIN_FILTER_SETTINGS')}
                  <div className="form-check form-switch">
                    <Form.Check
                      type="switch"
                      name="enabled_domain_filter"
                      id="enabled_domain_filter"
                      checked={values.enabled_domain_filter || false}
                      onChange={handleChange}
                      className="form-check-input-lg"
                    />
                    <Form.Label className="form-check-label fw-semibold text-secondary m-0" htmlFor='enabled_domain_filter'>
                      {values.enabled_domain_filter ? 'Enabled' : 'Disabled'}
                    </Form.Label>
                  </div>
								</div>
                <small className="text-muted">{t('TXT_DOMAIN_FILTER_DESCRIPTION')}</small>
              </div>
            </div>

          </div>
        </div>
      </div>

      {/* Domain Filter Content */}
      {values.enabled_domain_filter && (
				<Row className="g-3 ">
          {/* Allowed Domains Section */}
          <Col lg={6}>
            <Card className="h-100 border-0 ">
              <Card.Header className="bg-success bg-opacity-10 border-0 py-3">
                <div className="d-flex align-items-center">
                  <div className="icon-wrapper me-2">
                  </div>
                  <div className="flex-grow-1">
										<div className="fw-bold text-success mb-0">
											<i className="mdi mdi-check-circle text-success " style={{ fontSize: '18px', marginRight: '4px' }}></i>

											{t('LABEL_SEARCH_DOMAIN_FILTER')}
											<span>{`( ${values.search_domain_filter.length})`}</span>

										</div>
                    <small className="text-muted">{t('TXT_SEARCH_DOMAIN_HELP')}</small>
                  </div>
                  <i className="mdi mdi-information-outline text-muted" 
                     title={t('TXT_SEARCH_DOMAIN_HELP')} 
                     style={{ cursor: 'help' }}></i>
                </div>
              </Card.Header>
              <Card.Body className="p-3">
                {/* Combined Input + Tags Container */}
                <div 
                  className="form-control border-success border-opacity-50 p-2 d-flex flex-wrap align-items-center gap-2"
                  style={{ 
                    maxHeight: '200px',
                    overflowY: 'auto',
                    cursor: 'text'
                  }}
                  onClick={() => document.getElementById('searchDomainInput').focus()}
                >
                  {/* Existing Domain Tags */}
                  {values.search_domain_filter && values.search_domain_filter.map((domain, index) => (
                    <span 
                      key={index} 
                      className="badge bg-success bg-opacity-90 text-white rounded-pill px-2 py-1 d-flex align-items-center"
                      style={{ fontSize: '0.8rem', height: '24px' }}
                    >
                      {/* <i className="mdi mdi-web me-1" style={{ fontSize: '0.85rem' }}></i> */}
                      <span className="fw-medium">{domain}</span>
                      <button
                        type="button"
                        variant=""
                        className="btn st-btn-material-ico ms-1 ico-white"
                        style={{ fontSize: '0.5em', width: '12px', height: '12px', color: '#fff' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          removeSearchDomain(setFieldValue, values, index);
                        }}
                        aria-label="Remove domain"
                      >
                        <span className="mdi mdi-close"></span>
                      </button>
                    </span>
                  ))}
                  
                  {/* Input Field */}
                  <div className="flex-grow-1 position-relative" style={{ minWidth: '200px' }}>
                    <Form.Control
                      id="searchDomainInput"
                      type="text"
                      size="sm"
                      placeholder={values.search_domain_filter?.length ? "" : t('TXT_SEARCH_DOMAIN_PLACEHOLDER')}
                      value={currentSearchDomain}
                      onChange={(e) => setCurrentSearchDomain(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          addSearchDomain(setFieldValue, values);
                        }
                      }}
                      className="border-0 shadow-none"
                      style={{ 
                        backgroundColor: 'transparent',
                        outline: 'none',
                        fontSize: '0.875rem'
                      }}
                    />
                  </div>
                  
                  {/* Add Button - only show when typing */}
                  {currentSearchDomain.trim() && (
                    <Button
                      type="button"
                      size="sm"
                      variant="success"
                      onClick={() => addSearchDomain(setFieldValue, values)}
                      className="border-0 rounded-circle d-flex align-items-center justify-content-center ms-auto"
                      style={{ 
                        width: '24px', 
                        height: '24px',
                        fontSize: '12px'
                      }}
                    >
                      <i className="mdi mdi-plus"></i>
                    </Button>
                  )}
                  
                  {/* Empty State */}
                  {(!values.search_domain_filter || values.search_domain_filter.length === 0) && !currentSearchDomain && (
                    <div className="w-100 text-center text-muted py-3">
                      <i className="mdi mdi-web-plus me-1 opacity-50"></i>
                      <small>{t('TXT_NO_DOMAINS_ADDED')}</small>
                    </div>
                  )}
                </div>
                
              </Card.Body>
            </Card>
          </Col>

          {/* Blocked Domains Section */}
          <Col lg={6}>
            <Card className="h-100 border-0 ">
              <Card.Header className="bg-danger bg-opacity-10 border-0 py-3">
                <div className="d-flex align-items-center">
                  <div className="icon-wrapper me-2">
                  </div>
                  <div className="flex-grow-1">
										<div className="fw-bold text-danger mb-0">
											<i className="mdi mdi-block-helper text-danger " style={{ fontSize: '18px', marginRight: '4px' }}></i>

											{t('LABEL_EXCLUDED_DOMAIN_FILTER')}
											<span>{`( ${values.excluded_domain_filter.length})`}</span>

										</div>
                    <small className="text-muted">{t('TXT_EXCLUDED_DOMAIN_HELP')}</small>
                  </div>
                  <i className="mdi mdi-information-outline text-muted" 
                     title={t('TXT_EXCLUDED_DOMAIN_HELP')} 
                     style={{ cursor: 'help' }}></i>
                </div>
              </Card.Header>
              <Card.Body className="p-3">
                {/* Combined Input + Tags Container */}
                <div 
                  className="form-control border-danger border-opacity-50 p-2 d-flex flex-wrap align-items-center gap-2"
                  style={{ 
                    maxHeight: '200px',
                    overflowY: 'auto',
                    cursor: 'text'
                  }}
                  onClick={() => document.getElementById('excludedDomainInput').focus()}
                >
                  {/* Existing Domain Tags */}
                  {values.excluded_domain_filter && values.excluded_domain_filter.map((domain, index) => (
                    <span 
                      key={index} 
                      className="badge bg-danger bg-opacity-90 text-white rounded-pill px-2 py-1 d-flex align-items-center"
                      style={{ fontSize: '0.8rem', height: '24px' }}
                    >
                      {/* <i className="mdi mdi-web-off me-1" style={{ fontSize: '0.85rem' }}></i> */}
                      <span className="fw-medium">{domain}</span>
                      <button
                        type="button"
                        className="btn st-btn-material-ico ms-1 ico-white"
                        style={{ fontSize: '0.5em', width: '12px', height: '12px' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          removeExcludedDomain(setFieldValue, values, index);
                        }}
                        aria-label="Remove domain"
                      >

                        <span className="mdi mdi-close"></span>
                      </button>
                    </span>
                  ))}
                  
                  {/* Input Field */}
                  <div className="flex-grow-1 position-relative" style={{ minWidth: '200px' }}>
                    <Form.Control
                      id="excludedDomainInput"
                      type="text"
                      size="sm"
                      placeholder={values.excluded_domain_filter?.length ? "" : t('TXT_EXCLUDED_DOMAIN_PLACEHOLDER')}
                      value={currentExcludedDomain}
                      onChange={(e) => setCurrentExcludedDomain(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          addExcludedDomain(setFieldValue, values);
                        }
                      }}
                      className="border-0 shadow-none"
                      style={{ 
                        backgroundColor: 'transparent',
                        outline: 'none',
                        fontSize: '0.875rem'
                      }}
                    />
                  </div>
                  
                  {/* Add Button - only show when typing */}
                  {currentExcludedDomain.trim() && (
                    <Button
                      type="button"
                      size="sm"
                      variant="danger"
                      onClick={() => addExcludedDomain(setFieldValue, values)}
                      className="border-0 rounded-circle d-flex align-items-center justify-content-center ms-auto"
                      style={{ 
                        width: '24px', 
                        height: '24px',
                        fontSize: '12px'
                      }}
                    >
                      <i className="mdi mdi-plus"></i>
                    </Button>
                  )}
                  
                  {/* Empty State */}
                  {(!values.excluded_domain_filter || values.excluded_domain_filter.length === 0) && !currentExcludedDomain && (
                    <div className="w-100 text-center text-muted py-3">
                      <i className="mdi mdi-web-off me-1 opacity-50"></i>
                      <small>{t('TXT_NO_DOMAINS_ADDED')}</small>
                    </div>
                  )}
                </div>
                
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}
    </Card>
  );
};

export default DomainFilter;