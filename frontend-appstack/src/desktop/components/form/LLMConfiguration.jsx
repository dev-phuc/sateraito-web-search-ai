import { useState, useEffect, useCallback, useRef } from 'react';
import { useTranslation } from 'react-i18next';

import * as Yup from "yup";
// Library UI imports
import { Formik } from "formik";
import { Form, Button, Modal, Spinner, Row, Col, Card } from "react-bootstrap";

// Hook components
import useTheme from '@/hooks/useTheme'

// Components
import DomainFilter from './DomainFilter';

// Zustand
import useStoreLLMConfiguration from '@/store/llm_configuration';

// Constants
import { LLM_CONFIGURATION_DEFAULT } from '@/constants';
import { faHandsAslInterpreting } from '@fortawesome/free-solid-svg-icons';

const LLMConfigurationForm = ({ tenant, app_id, onCancel, afterSubmit }) => {
  // Default hooks
  const { t } = useTranslation();
  const { showNotice } = useTheme();
  const RESPONSE_LIST = [
    { value: 'low', label: t('LABEL_RESPONSE_LOW'), icon: 'mdi mdi-speedometer-slow' },
    { value: 'medium', label: t('LABEL_RESPONSE_MEDIUM'), icon: 'mdi mdi-speedometer-medium' },
    { value: 'high', label: t('LABEL_RESPONSE_HIGH'), icon: 'mdi mdi-speedometer' },
  ];
  // State
  const [loading, setLoading] = useState({ submitting: false });
  const submittingRef = useRef(false);
  const [showConfirmResetDefaults, setShowConfirmResetDefaults] = useState(false);
  const [responseState, setResponseState] = useState('low');

  // Zustand stores
  const { llmConfiguration, editLLMConfiguration } = useStoreLLMConfiguration();

  // Sync responseState with form values
  useEffect(() => {
    if (llmConfiguration?.response_length_level) {
      setResponseState(llmConfiguration.response_length_level);
    }
  }, [llmConfiguration]);

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
                  <div className="model-intro ">
                    <div className="intro-header">Current Plan</div>
                    <div className="">
                      <div className="d-flex align-items-center gap-2">
                        <span className="sub-text">{t('LABEL_MODEL_NAME')}</span>
                      </div>
                      <span className="badge ai-model px-2 py-1 rounded-pill small chip">
                        <i className="mdi mdi-robot me-2"></i>
                        <span className="fw-semibold">{values.model_name}</span>
                      </span>
                    </div>

                    {/* <Form.Group>
                    <Form.Label className="mb-0 me-2 fw-semibold text-secondary">
                      <span className='me-2 mdi mdi-chart-bubble'></span>
                      {t('LABEL_MODEL_NAME')}
                    </Form.Label>
                    <Form.Control
                      type="text"
                      name="model_name"
                      value={values.model_name}
                      onChange={handleChange}
                      isInvalid={touched.model_name && !!errors.model_name}
                      placeholder={t('TXT_MODEL_NAME_PLACEHOLDER')}
                      readOnly
                      disabled
                      className="d-none"
                    />
                    <Form.Control.Feedback type="invalid">{touched.model_name && errors.model_name}</Form.Control.Feedback>
                  </Form.Group> */}
                    <div className="response-level-section">
                      <div className="d-flex flex-column falign-items-start ">
                        <div className="d-flex align-items-center gap-2 mb-2 mb-lg-0">
                          <span className="sub-text">{t('LABEL_RESPONSE_LENGTH_LEVEL')}</span>
                        </div>
                        <div className="d-flex flex-wrap gap-2">
                          {RESPONSE_LIST.map((item) => (
                            <button
                              key={item.value}
                              type="button"
                              className={`btn st-btn-material-outline rounded-pill d-flex align-items-center quick-filter-chip ${values.response_length_level} ${item.value === values.response_length_level
                                  ? ' text-white shadow-sm active'
                                  : ' bg-white text-info border-info border-opacity-50 hover-lift'
                                }`}
                              style={{
                                fontSize: '0.85rem',
                                fontWeight: '500',
                                transition: 'all 0.2s ease-in-out',
                              }}
                              onClick={() => {
                                setResponseState(item.value);
                                setFieldValue('response_length_level', item.value);
                              }}
                            >
                              <i className={item.icon} style={{ fontSize: '1.1rem' }}></i>
                              <span>{item.label}</span>
                              {item.value === values.response_length_level && (
                                <i className="mdi mdi-check-circle ms-1" style={{ fontSize: '0.9rem' }}></i>
                              )}
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                  <Form.Group>
                    <Form.Label className="fw-bold text-base mb-1 d-flex align-items-center sub-text">
                      {/* <span className='me-2 mdi mdi-message-text'></span> */}
                      {t('LABEL_SYSTEM_PROMPT')}
                    </Form.Label>
                    <Form.Control
                      as="textarea"
                      rows={12}
                      name="system_prompt"
                      value={values.system_prompt || ''}
                      onChange={handleChange}
                      placeholder={t('TXT_SYSTEM_PROMPT_PLACEHOLDER')}
                      className="dashboard-promt"
                    />
                  </Form.Group>
                </Col>

                <DomainFilter 
                  values={values}
                  handleChange={handleChange}
                  setFieldValue={setFieldValue}
                />
              </Row>
            </Card>

            {/* Form actions */}
            <Col md={6} className="action-buttons " >
              <Row className="mt-3">
                <Col lg="8" className="mb-3 mb-lg-0">
                  <div className="d-flex flex-column flex-sm-row gap-2">
                    <Button className="btn st-btn-material" variant='' type="submit" disabled={loading.submitting || !isValid || (!dirty && !isSubmitting)} aria-busy={loading.submitting}>
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
                    <Button className="btn st-btn-material-outline" variant="" disabled={loading.submitting} onClick={() => resetForm()}>
                      <i className="mdi mdi-restore"></i>
                      <span className="ms-2">{t('BTN_RESET')}</span>
                    </Button>
                  </div>
                </Col>
                <Col lg="4">
                  <div className="d-flex justify-content-lg-end">
                    <Button className="btn st-btn-material-outline" variant=""  onClick={() => setShowConfirmResetDefaults(true)} disabled={loading.submitting || showConfirmResetDefaults} >
                      <i className="mdi mdi-backup-restore"></i>
                      <span className="ms-2">{t('BTN_RESET_TO_DEFAULTS')}</span>
                    </Button>
                  </div>
                </Col>
                <Col md="12">
                  <Form.Text className="d-block text-muted mt-2">{t('TXT_FORM_SUBMIT_CONDITION')}</Form.Text>
                </Col>
              </Row>
            </Col>
            
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