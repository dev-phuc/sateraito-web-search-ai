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

const LLMConfigurationForm = ({ tenant, app_id, onCancel, afterSubmit }) => {
  // Default hooks
  const { t } = useTranslation();
  const { showNotice } = useTheme();

  // State
  const [loading, setLoading] = useState({ submitting: false });
  const submittingRef = useRef(false);
  const [showConfirmResetDefaults, setShowConfirmResetDefaults] = useState(false);

  // Zustand stores
  const { llmConfiguration, editLLMConfiguration } = useStoreLLMConfiguration();

  const validationSchema = Yup.object().shape({
    model_name: Yup.string().required(t('MSG_ERROR_MODEL_NAME_REQUIRED')),
    system_prompt: Yup.string().nullable(),
    response_length_level: Yup.string().oneOf(['low', 'medium', 'high']).required(t('MSG_ERROR_RESPONSE_LENGTH_LEVEL_REQUIRED'))
  });

  // Constant value (use provided data if available)
  const initialValues = llmConfiguration;

  const handlerOnSubmit = useCallback(async (values, { setSubmitting }) => {
    if (submittingRef.current) return;
    submittingRef.current = true;
    setLoading(l => ({ ...l, submitting: true }));

    try {
      const result = await editLLMConfiguration(tenant, app_id, values);
      const { success, error } = result;
      let message = '';
      if (success) {
        message = t('TXT_UPDATE_LLM_CONFIGURATION_SUCCESS');
        showNotice('success', message);

        if (afterSubmit) {
          afterSubmit(success);
        }
      } else {
        message = t(error);
        if (message === error) {
          message = t('TXT_ERROR_UPDATE_LLM_CONFIGURATION');
        }
        showNotice('error', message);
      }
    } finally {
      submittingRef.current = false;
      setLoading(l => ({ ...l, submitting: false }));
      if (setSubmitting) setSubmitting(false);
    }

  }, [editLLMConfiguration, tenant, app_id, afterSubmit, t, showNotice]);

  const handlerResetToDefaults = async () => {
    setShowConfirmResetDefaults(false);
    if (submittingRef.current) return;
    submittingRef.current = true;
    setLoading(l => ({ ...l, submitting: true }));
    try {
      const result = await editLLMConfiguration(tenant, app_id, LLM_CONFIGURATION_DEFAULT);
      const { success, error } = result;
      let message = '';
      if (success) {
        if (afterSubmit) {
          afterSubmit(success);
        }
        message = t('TXT_RESET_LLM_CONFIGURATION_SUCCESS');
        showNotice('success', message);
      } else {
        message = t(error);
        if (message === error) {
          message = t('TXT_ERROR_RESET_LLM_CONFIGURATION');
        }
        showNotice('error', message);
      }
    } finally {
      submittingRef.current = false;
      setLoading(l => ({ ...l, submitting: false }));
    }
  };

  if (!llmConfiguration) {
    return <div>Loading...</div>;
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
                      <option value="high">{t('LABEL_RESPONSE_LONG')}</option>
                    </Form.Select>
                    <Form.Control.Feedback type="invalid">{touched.response_length_level && errors.response_length_level}</Form.Control.Feedback>
                  </Form.Group>
                </Col>
                <Col md={12} className="mb-3">
                  <Form.Group>
                    <Form.Label>{t('LABEL_SYSTEM_PROMPT')}</Form.Label>
                    <Form.Control
                      as="textarea"
                      rows={11}
                      name="system_prompt"
                      value={values.system_prompt || ''}
                      onChange={handleChange}
                      placeholder={t('TXT_SYSTEM_PROMPT_PLACEHOLDER')}
                    />
                  </Form.Group>
                </Col>
              </Row>
            </Card>
            <div className='px-3 mx-2 mb-3'>
              <Row className="mt-3">
                <Col md="8">
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
                  {onCancel && <Button variant="secondary" onClick={onCancel} className="ms-2">{t('BTN_CANCEL')}</Button>}
                  <Button variant="outline-secondary" disabled={loading.submitting} onClick={() => resetForm()} className="ms-2">
                    <i className="mdi mdi-restore"></i>
                    <span className="ms-2">{t('BTN_RESET')}</span>
                  </Button>
                </Col>
                <Col md="4">
                  <div className="d-flex justify-content-end">
                    <Button variant="outline-danger" onClick={() => setShowConfirmResetDefaults(true)} disabled={loading.submitting || showConfirmResetDefaults}>
                      <i className="mdi mdi-backup-restore"></i>
                      <span className="ms-2">{t('BTN_RESET_TO_DEFAULTS')}</span>
                    </Button>
                  </div>
                </Col>
                <Form.Text className="d-block text-muted mt-2">{t('TXT_FORM_SUBMIT_CONDITION')}</Form.Text>
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