import { useState, useEffect, useCallback, useRef } from 'react';
import { useTranslation } from 'react-i18next';

import * as Yup from "yup";
// Library UI imports
import { Formik } from "formik";
import { Form, Button, Modal, Spinner, Row, Col, Card } from "react-bootstrap";

// Hook components
import useTheme from '@/hooks/useTheme'

// Zustand
import useStoreLLMConfiguration from '@/store/llm_configuration';

// Constants
import { LLM_CONFIGURATION_DEFAULT } from '@/constants';
import { faHandsAslInterpreting } from '@fortawesome/free-solid-svg-icons';

// Utils
import { validateDomainOrUrl } from '@/utils';

const LLMConfigurationForm = ({ tenant, app_id, onCancel, afterSubmit }) => {
  // Default hooks
  const { t } = useTranslation();
  const { showNotice } = useTheme();

  // State
  const [loading, setLoading] = useState({ submitting: false });
  const submittingRef = useRef(false);
  const [showConfirmResetDefaults, setShowConfirmResetDefaults] = useState(false);
  const [currentSearchDomain, setCurrentSearchDomain] = useState('');
  const [currentExcludedDomain, setCurrentExcludedDomain] = useState('');

  // Zustand stores
  const { llmConfiguration, editLLMConfiguration } = useStoreLLMConfiguration();

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
      // showNotice('success', t('MSG_SUCCESS_DOMAIN_ADDED'));
    }
  };

  const removeSearchDomain = (setFieldValue, values, indexToRemove) => {
    const currentDomains = values.search_domain_filter || [];
    setFieldValue('search_domain_filter', currentDomains.filter((_, index) => index !== indexToRemove));
    // showNotice('success', t('MSG_INFO_DOMAIN_REMOVED'));
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
      // showNotice('success', t('MSG_SUCCESS_DOMAIN_ADDED'));
    }
  };

  const removeExcludedDomain = (setFieldValue, values, indexToRemove) => {
    const currentDomains = values.excluded_domain_filter || [];
    setFieldValue('excluded_domain_filter', currentDomains.filter((_, index) => index !== indexToRemove));
    // showNotice('success', t('MSG_INFO_DOMAIN_REMOVED'));
  };

  const validationSchema = Yup.object().shape({
    model_name: Yup.string().required(t('MSG_ERROR_MODEL_NAME_REQUIRED')),
    system_prompt: Yup.string().nullable(),
    response_length_level: Yup.string().oneOf(['low', 'medium', 'high']).required(t('MSG_ERROR_RESPONSE_LENGTH_LEVEL_REQUIRED')),
    enabled_domain_filter: Yup.boolean().nullable(),
    search_domain_filter: Yup.array().of(Yup.string()).nullable(),
    excluded_domain_filter: Yup.array().of(Yup.string()).nullable(),
  });

  // Constant value (use provided data if available)
  const initialValues = llmConfiguration;

  const handlerOnSubmit = useCallback(async (values, { setSubmitting }) => {
    if (submittingRef.current) return;
    submittingRef.current = true;
    setLoading(temp => ({ ...temp, submitting: true }));

    try {
      const { success, message } = await editLLMConfiguration(tenant, app_id, values);
      if (success) {
        if (afterSubmit) {
          afterSubmit(success);
        }
        showNotice('success', t('TXT_UPDATE_LLM_CONFIGURATION_SUCCESS'));
      } else {
        let messageNotice = t(message);
        if (messageNotice === message) {
          messageNotice = t('TXT_ERROR_UPDATE_LLM_CONFIGURATION');
        }
        showNotice('error', messageNotice);
      }
    } finally {
      submittingRef.current = false;
      setLoading(temp => ({ ...temp, submitting: false }));
      if (setSubmitting) setSubmitting(false);
    }

  }, [editLLMConfiguration, tenant, app_id, afterSubmit, t, showNotice]);

  const handlerResetToDefaults = async () => {
    setShowConfirmResetDefaults(false);
    if (submittingRef.current) return;
    submittingRef.current = true;
    setLoading(l => ({ ...l, submitting: true }));
    try {
      const { success, message } = await editLLMConfiguration(tenant, app_id, LLM_CONFIGURATION_DEFAULT);
      if (success) {
        if (afterSubmit) {
          afterSubmit(success);
        }
        showNotice('success', t('TXT_RESET_LLM_CONFIGURATION_SUCCESS'));
      } else {
        let messageNotice = t(message);
        if (messageNotice === message) {
          messageNotice = t('TXT_ERROR_UPDATE_LLM_CONFIGURATION');
        }
        showNotice('error', messageNotice);
      }
    } finally {
      submittingRef.current = false;
      setLoading(l => ({ ...l, submitting: false }));
    }
  };

  if (loading && !llmConfiguration) {
    return (
      <div className="text-center my-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">{t('TXT_LOADING')}</span>
        </Spinner>
      </div>
    )
  }

  // Return the component
  return (
    <Formik
      initialValues={initialValues}
      enableReinitialize
      validationSchema={validationSchema}
      onSubmit={handlerOnSubmit}
    >
      {({ values, handleChange, handleSubmit, setFieldValue, errors, touched, isValid, dirty, isSubmitting, resetForm }) => {
        return (
          <Form onSubmit={handleSubmit} noValidate className=''>
            <Card className='shadow-none mx-2 mt-2 mb-3'>
              <Row>
                <Col md={12} className="mb-3">
                  <Form.Group>
                    <Form.Label>{t('LABEL_SYSTEM_PROMPT')}</Form.Label>
                    <Form.Control
                      as="textarea"
                      rows={9}
                      name="system_prompt"
                      value={values.system_prompt || ''}
                      onChange={handleChange}
                      placeholder={t('TXT_SYSTEM_PROMPT_PLACEHOLDER')}
                    />
                  </Form.Group>
                </Col>
                <Col md={6} className="mb-3">
                  <Form.Group>
                    <Form.Label>{t('LABEL_MODEL_NAME')}</Form.Label>
                    <Form.Control
                      type="text"
                      name="model_name"
                      value={values.model_name}
                      onChange={handleChange}
                      isInvalid={touched.model_name && !!errors.model_name}
                      placeholder={t('TXT_MODEL_NAME_PLACEHOLDER')}
                      readOnly
                      disabled
                    />
                    <Form.Control.Feedback type="invalid">{touched.model_name && errors.model_name}</Form.Control.Feedback>
                  </Form.Group>
                </Col>
                <Col md={6} className="mb-3">
                  <Form.Group>
                    <Form.Label>{t('LABEL_RESPONSE_LENGTH_LEVEL')}</Form.Label>
                    <Form.Select
                      name="response_length_level"
                      value={values.response_length_level}
                      onChange={handleChange}
                      isInvalid={touched.response_length_level && !!errors.response_length_level}
                    >
                      <option value="low">{t('LABEL_RESPONSE_SHORT')}</option>
                      <option value="medium">{t('LABEL_RESPONSE_MEDIUM')}</option>
                      <option value="high">{t('LABEL_RESPONSE_HIGH')}</option>
                    </Form.Select>
                    <Form.Control.Feedback type="invalid">{touched.response_length_level && errors.response_length_level}</Form.Control.Feedback>
                  </Form.Group>
                </Col>
                <Col md={12} className="mb-4">
                  <Form.Group>
                    <Form.Label>{t('LABEL_DOMAIN_FILTER_SETTINGS')}</Form.Label>
                    <div className="d-flex align-items-center mb-2">
                      <Form.Check
                        type="checkbox"
                        name="enabled_domain_filter"
                        id="enabled_domain_filter"
                        checked={values.enabled_domain_filter || false}
                        onChange={handleChange}
                      />
                      <Form.Label className="mb-0 ms-1 me-2" htmlFor='enabled_domain_filter'>
                        {t('LABEL_ENABLED_DOMAIN_FILTER')}
                      </Form.Label>
                      <i className="mdi mdi-information-outline text-muted"
                        title={t('TXT_DOMAIN_FILTER_DESCRIPTION')}
                        style={{ cursor: 'help' }}>
                      </i>
                    </div>
                    <Form.Text className="text-muted">
                      {t('TXT_DOMAIN_FILTER_DESCRIPTION')}
                    </Form.Text>
                  </Form.Group>
                </Col>

                {values.enabled_domain_filter && (
                  <>
                    <Col md={12} className="mb-4">
                      <Card className="border-success border-opacity-25 bg-light bg-opacity-50">
                        <Card.Body className="p-3">
                          <Form.Group>
                            <div className="d-flex align-items-center mb-2">
                              <Form.Label className="mb-0 me-2 fw-semibold text-success">
                                <i className="mdi mdi-check-circle me-1"></i>
                                {t('LABEL_SEARCH_DOMAIN_FILTER')}
                              </Form.Label>
                              <i className="mdi mdi-information-outline text-muted" title={t('TXT_SEARCH_DOMAIN_HELP')} style={{ cursor: 'help' }}></i>
                            </div>

                            <Row>
                              <Col md="6">
                                <Form.Text className="text-muted mb-2 d-block">
                                  {t('TXT_SEARCH_DOMAIN_HELP')}
                                </Form.Text>
                                <div className="d-flex flex-column flex-sm-row">
                                  <Form.Control
                                    type="text"
                                    placeholder={t('TXT_SEARCH_DOMAIN_PLACEHOLDER')}
                                    value={currentSearchDomain}
                                    onChange={(e) => setCurrentSearchDomain(e.target.value)}
                                    onKeyPress={(e) => {
                                      if (e.key === 'Enter') {
                                        e.preventDefault();
                                        addSearchDomain(setFieldValue, values);
                                      }
                                    }}
                                    className="border-success border-opacity-50 mb-2 mb-sm-0"
                                  />
                                  <Button
                                    type="button"
                                    variant="outline-success"
                                    className="ms-sm-2 px-3 d-flex align-items-center justify-content-center"
                                    onClick={() => addSearchDomain(setFieldValue, values)}
                                    disabled={!currentSearchDomain.trim()}
                                  >
                                    <i className="mdi mdi-plus me-1 d-sm-none"></i>
                                    <i className="mdi mdi-plus d-none d-sm-inline"></i>
                                    <span className="d-sm-none">Add Domain</span>
                                  </Button>
                                </div>
                              </Col>

                              <Col md="6">
                                {values.search_domain_filter && values.search_domain_filter.length > 0 ? (
                                  <div>
                                    <small className="text-muted d-block">
                                      <i className="mdi mdi-label-outline me-1"></i>
                                      {/* Allowed domains ({values.search_domain_filter.length}): */}
                                      {t('LABEL_ALLOWED_DOMAINS', { count: values.search_domain_filter.length })}
                                    </small>
                                    <div className="d-flex flex-wrap gap-2">
                                      {values.search_domain_filter.map((domain, index) => (
                                        <span key={index} className="badge bg-success bg-opacity-90 fs-6 d-flex align-items-center">
                                          <i className="mdi mdi-web me-1"></i>
                                          {domain}
                                          <button
                                            type="button"
                                            className="btn-close btn-close-white ms-2"
                                            style={{ fontSize: '0.7em' }}
                                            onClick={() => removeSearchDomain(setFieldValue, values, index)}
                                            aria-label="Remove domain"
                                          ></button>
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                ) : (
                                  <div className="text-center text-muted">
                                    <i className="mdi mdi-inbox-outline me-1"></i>
                                    <small>{t('TXT_NO_DOMAINS_ADDED')}</small>
                                  </div>
                                )}
                              </Col>

                            </Row>
                          </Form.Group>
                        </Card.Body>
                      </Card>
                    </Col>

                    <Col md={12} className="mb-4">
                      <Card className="border-danger border-opacity-25 bg-light bg-opacity-50">
                        <Card.Body className="p-3">
                          <Form.Group>
                            <div className="d-flex align-items-center mb-2">
                              <Form.Label className="mb-0 me-2 fw-semibold text-danger">
                                <i className="mdi mdi-block-helper me-1"></i>
                                {t('LABEL_EXCLUDED_DOMAIN_FILTER')}
                              </Form.Label>
                              <i className="mdi mdi-information-outline text-muted" title={t('TXT_EXCLUDED_DOMAIN_HELP')} style={{ cursor: 'help' }}></i>
                            </div>

                            <Row>
                              <Col md="6">
                                <Form.Text className="text-muted mb-2 d-block">
                                  {t('TXT_EXCLUDED_DOMAIN_HELP')}
                                </Form.Text>
                                <div className="d-flex flex-column flex-sm-row">
                                  <Form.Control
                                    type="text"
                                    placeholder={t('TXT_EXCLUDED_DOMAIN_PLACEHOLDER')}
                                    value={currentExcludedDomain}
                                    onChange={(e) => setCurrentExcludedDomain(e.target.value)}
                                    onKeyPress={(e) => {
                                      if (e.key === 'Enter') {
                                        e.preventDefault();
                                        addExcludedDomain(setFieldValue, values);
                                      }
                                    }}
                                    className="border-danger border-opacity-50 mb-2 mb-sm-0"
                                  />
                                  <Button
                                    type="button"
                                    variant="outline-danger"
                                    className="ms-sm-2 px-3 d-flex align-items-center justify-content-center"
                                    onClick={() => addExcludedDomain(setFieldValue, values)}
                                    disabled={!currentExcludedDomain.trim()}
                                  >
                                    <i className="mdi mdi-plus me-1 d-sm-none"></i>
                                    <i className="mdi mdi-plus d-none d-sm-inline"></i>
                                    <span className="d-sm-none">Add Domain</span>
                                  </Button>
                                </div>
                              </Col>

                              <Col md="6">
                                {values.excluded_domain_filter && values.excluded_domain_filter.length > 0 ? (
                                  <div>
                                    <small className="text-muted d-block">
                                      <i className="mdi mdi-label-outline me-1"></i>
                                      {t('LABEL_BLOCKED_DOMAINS', { count: values.excluded_domain_filter.length })}
                                    </small>
                                    <div className="d-flex flex-wrap gap-2">
                                      {values.excluded_domain_filter.map((domain, index) => (
                                        <span key={index} className="badge bg-danger bg-opacity-90 fs-6 d-flex align-items-center">
                                          <i className="mdi mdi-web-off me-1"></i>
                                          {domain}
                                          <button
                                            type="button"
                                            className="btn-close btn-close-white ms-2"
                                            style={{ fontSize: '0.7em' }}
                                            onClick={() => removeExcludedDomain(setFieldValue, values, index)}
                                            aria-label="Remove domain"
                                          ></button>
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                ) : (
                                  <div className="text-center text-muted">
                                    <i className="mdi mdi-inbox-outline me-1"></i>
                                    <small>{t('TXT_NO_DOMAINS_ADDED')}</small>
                                  </div>
                                )}
                              </Col>

                            </Row>
                          </Form.Group>
                        </Card.Body>
                      </Card>
                    </Col>
                  </>
                )}
              </Row>
            </Card>

            {/* Form actions */}
            <div className='px-3 mx-2 mb-3'>
              <Row className="mt-3">
                <Col lg="8" className="mb-3 mb-lg-0">
                  <div className="d-flex flex-column flex-sm-row gap-2">
                    <Button type="submit" disabled={loading.submitting || !isValid || (!dirty && !isSubmitting)} aria-busy={loading.submitting}>
                      {loading.submitting ? (
                        <>
                          <i className="mdi mdi-spin mdi-loading"></i>
                          <span className="ms-2">{t('TXT_LOADING')}</span>
                        </>
                      ) :
                        <>
                          <i className="mdi mdi-content-save"></i>
                          <span className="ms-2">{t('BTN_SUBMIT')}</span>
                        </>
                      }
                    </Button>
                    {onCancel && <Button variant="secondary" onClick={onCancel}>{t('BTN_CANCEL')}</Button>}
                    <Button variant="outline-secondary" disabled={loading.submitting} onClick={() => resetForm()}>
                      <i className="mdi mdi-restore"></i>
                      <span className="ms-2">{t('BTN_RESET')}</span>
                    </Button>
                  </div>
                </Col>
                <Col lg="4">
                  <div className="d-flex justify-content-lg-end">
                    <Button variant="outline-danger" onClick={() => setShowConfirmResetDefaults(true)} disabled={loading.submitting || showConfirmResetDefaults} className="w-100 w-lg-auto">
                      <i className="mdi mdi-backup-restore"></i>
                      <span className="ms-2">{t('BTN_RESET_TO_DEFAULTS')}</span>
                    </Button>
                  </div>
                </Col>
                <Col md="12">
                  <Form.Text className="d-block text-muted mt-2">{t('TXT_FORM_SUBMIT_CONDITION')}</Form.Text>
                </Col>
              </Row>
            </div>
            
            {/* Modal for confirm reset to defaults */}
            <Modal show={showConfirmResetDefaults} onHide={() => setShowConfirmResetDefaults(false)} centered>
              <Modal.Header closeButton>
                <Modal.Title>{t('MODAL_TITLE_CONFIRM_RESET_TO_DEFAULTS')}</Modal.Title>
              </Modal.Header>
              <Modal.Body>
                <p>{t('MODAL_TEXT_CONFIRM_RESET_TO_DEFAULTS')}</p>
              </Modal.Body>
              <Modal.Footer>
                <Button variant="secondary" onClick={() => setShowConfirmResetDefaults(false)}>
                  {t('BTN_CANCEL')}
                </Button>
                <Button variant="danger" onClick={handlerResetToDefaults}>
                  {t('BTN_RESET_TO_DEFAULTS')}
                </Button>
              </Modal.Footer>
            </Modal>
          </Form>
        )
      }}
    </Formik>
  );
};

export default LLMConfigurationForm;