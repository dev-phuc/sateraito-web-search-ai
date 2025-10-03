import { useState, useEffect, useCallback, useRef } from 'react';
import { useTranslation } from 'react-i18next';

import * as Yup from "yup";
// Library UI imports
import { Formik } from "formik";
import { Form, Button, InputGroup, Modal, Row, Col, Card } from "react-bootstrap";

// Components
import Loader from '@/desktop/components/Loader';

// Hook components
import useTheme from '@/hooks/useTheme'

// Zustand
import useStoreBoxSearchConfig from '@/store/box_search_config';

// Constants
import { BOX_SEARCH_DESIGN_DEFAULT } from '@/constants';
import style from './Style.scss';
const BoxSearchConfigForm = ({ tenant, app_id, data, onCancel, afterSubmit }) => {
  // Default hooks
  const { t } = useTranslation();
  const { showNotice } = useTheme();

  // State
  const [loading, setLoading] = useState({ submitting: false });
  const [showConfirmResetDefaults, setShowConfirmResetDefaults] = useState(false);
  const submittingRef = useRef(false);

  // Zustand stores
  const { boxSearchConfig, setBoxSearchConfigPreview, editBoxSearchConfig } = useStoreBoxSearchConfig();

  const validationSchema = Yup.object().shape({
    search_box: Yup.object().shape({
      type: Yup.string().oneOf(['box', 'fullscreen', 'fullscreen_blur']).required(),
      options: Yup.object().shape({
        background_color: Yup.string().required(),
        shadow: Yup.boolean(),
        border_radius: Yup.number().min(0),
        padding: Yup.number().min(0),
        // keep font-size as string if present in default, but accept number too
        ['font-size']: Yup.mixed().test('is-number-or-string', 'Invalid font size', value => {
          return value === undefined || value === null || typeof value === 'string' || typeof value === 'number';
        })
      })
    }),
    search_button: Yup.object().shape({
      icon: Yup.string(),
      color: Yup.string(),
      background_color: Yup.string(),
      border_radius: Yup.number().min(0)
    }),
    theme: Yup.object().shape({
      color: Yup.string(),
      font: Yup.string()
    })
  });

  // Constant value (use provided data if available)
  const initialValues = boxSearchConfig;

  const handlerOnChange = (values) => {
    setBoxSearchConfigPreview(values);
  }

  const handlerOnSubmit = useCallback(async (values, { setSubmitting }) => {
    if (submittingRef.current) return;
    submittingRef.current = true;
    setLoading(l => ({ ...l, submitting: true }));

    try {
      const result = await editBoxSearchConfig(tenant, app_id, values);
      const { success, error } = result;
      let message = '';
      if (success) {
        message = t('TXT_UPDATE_BOX_SEARCH_CONFIG_SUCCESS');
        showNotice('success', message);

        if (afterSubmit) {
          afterSubmit(success);
        }
      } else {
        message = t(error);
        if (message === error) {
          message = t('TXT_ERROR_UPDATE_BOX_SEARCH_CONFIG');
        }
        showNotice('error', message);
      }
    } finally {
      submittingRef.current = false;
      setLoading(l => ({ ...l, submitting: false }));
      if (setSubmitting) setSubmitting(false);
    }

  }, [editBoxSearchConfig, tenant, app_id, afterSubmit, t, showNotice]);

  const handlerResetToDefaults = async () => {
    setShowConfirmResetDefaults(false);
    if (submittingRef.current) return;
    submittingRef.current = true;
    setLoading(l => ({ ...l, submitting: true }));
    try {
      const result = await editBoxSearchConfig(tenant, app_id, BOX_SEARCH_DESIGN_DEFAULT);
      const { success, error } = result;
      let message = '';
      if (success) {
        if (afterSubmit) {
          afterSubmit(success);
        }
        message = t('TXT_RESET_BOX_SEARCH_CONFIG_SUCCESS');
        showNotice('success', message);
      } else {
        message = t(error);
        if (message === error) {
          message = t('TXT_ERROR_RESET_BOX_SEARCH_CONFIG');
        }
        showNotice('error', message);
      }
    } finally {
      submittingRef.current = false;
      setLoading(l => ({ ...l, submitting: false }));
    }
  };

  if (!boxSearchConfig) {
    return <Loader />;
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

        useEffect(() => {
          handlerOnChange(values);
        }, [values]);

        return (
          <Form onSubmit={handleSubmit} noValidate className='box-search-config'>
            {/* Search Box Layout Section */}
            <div className="config-section">
              <div className="section-header">
                <i className="mdi mdi-view-dashboard section-icon"></i>
                <h5 className="section-title">{t('LABEL_SEARCH_BOX')} {t('LABEL_LAYOUT')}</h5>
              </div>

              <div className="form-group-compact">
                <Form.Label className="mb-2">{t('LABEL_TYPE')}</Form.Label>
                <div className="radio-group-modern">
                  <Form.Check
                    type="radio"
                    id="search_box_type_box"
                    name="search_box.type"
                    label={t('LABEL_BOX')}
                    value="box"
                    checked={values.search_box.type === "box"}
                    onChange={() => setFieldValue('search_box.type', 'box')}
                    isInvalid={touched.search_box?.type && !!errors.search_box?.type}
                  />
                  <Form.Check
                    type="radio"
                    id="search_box_type_fullscreen"
                    name="search_box.type"
                    label={t('LABEL_FULLSCREEN')}
                    value="fullscreen"
                    checked={values.search_box.type === "fullscreen"}
                    onChange={() => setFieldValue('search_box.type', 'fullscreen')}
                    isInvalid={touched.search_box?.type && !!errors.search_box?.type}
                  />
                  <Form.Check
                    type="radio"
                    id="search_box_type_fullscreen_blur"
                    name="search_box.type"
                    label={t('LABEL_FULLSCREEN_BLUR')}
                    value="fullscreen_blur"
                    checked={values.search_box.type === "fullscreen_blur"}
                    onChange={() => setFieldValue('search_box.type', 'fullscreen_blur')}
                    isInvalid={touched.search_box?.type && !!errors.search_box?.type}
                  />
                </div>
                <Form.Control.Feedback type="invalid">{touched.search_box?.type && errors.search_box?.type}</Form.Control.Feedback>
                <Form.Text>{t('TXT_CHOOSE_SEARCH_UI')}</Form.Text>
              </div>
            </div>

            {/* Appearance & Colors Section */}
            <div className="config-section">
              <div className="section-header">
                <i className="mdi mdi-palette section-icon"></i>
                <h5 className="section-title">{t('LABEL_APPEARANCE')} & {t('LABEL_COLOR')}</h5>
              </div>

              <Row>
                <Col lg={6} className="mb-3">
                  <Form.Label>{t('LABEL_COLOR')} ({t('LABEL_TEXT')})</Form.Label>
                  <div className="color-input-wrapper">
                    <Form.Control 
                      type="color" 
                      name="theme.color" 
                      value={values.theme.color} 
                      onChange={(e) => setFieldValue('theme.color', e.target.value)} 
                    />
                    <div className="color-preview" style={{ backgroundColor: values.theme.color }}></div>
                  </div>
                  <Form.Text>{t('TXT_TEXT_COLOR')}</Form.Text>
                </Col>

                <Col lg={6} className="mb-3">
                  <Form.Label>{t('LABEL_BACKGROUND_COLOR')}</Form.Label>
                  <div className="color-input-wrapper">
                    <Form.Control 
                      type="color" 
                      name="search_box.options.background_color" 
                      value={values.search_box.options.background_color} 
                      onChange={(e) => setFieldValue('search_box.options.background_color', e.target.value)} 
                      isInvalid={touched.search_box?.options?.background_color && !!errors.search_box?.options?.background_color} 
                    />
                    <div className="color-preview" style={{ backgroundColor: values.search_box.options.background_color }}></div>
                  </div>
                  <Form.Control.Feedback type="invalid">{touched.search_box?.options?.background_color && errors.search_box?.options?.background_color}</Form.Control.Feedback>
                  <Form.Text>{t('TXT_PICK_BACKGROUND_COLOR')}</Form.Text>
                </Col>

                <Col lg={12} className="mb-3">
                  <Form.Label>{t('LABEL_FONT')}</Form.Label>
                  <Form.Control 
                    type="text" 
                    name="theme.font" 
                    value={values.theme.font} 
                    onChange={(e) => setFieldValue('theme.font', e.target.value)} 
                    placeholder={t('TXT_FONT_PLACEHOLDER')} 
                  />
                  <Form.Text>{t('TXT_FONT_DESC')}</Form.Text>
                </Col>

                <Col lg={12}>
                  <div className="switch-wrapper">
                    <label className="switch-label">{t('LABEL_SHADOW')}</label>
                    <Form.Check 
                      type="switch" 
                      name="search_box.options.shadow" 
                      checked={values.search_box.options.shadow} 
                      onChange={(e) => setFieldValue('search_box.options.shadow', e.target.checked)} 
                    />
                  </div>
                  <Form.Text>{t('TXT_ENABLE_SHADOW')}</Form.Text>
                </Col>
              </Row>
            </div>

            {/* Dimensions & Spacing Section */}
            <div className="config-section">
              <div className="section-header">
                <i className="mdi mdi-resize section-icon"></i>
                <h5 className="section-title">{t('LABEL_DIMENSIONS')} & {t('LABEL_SPACING')}</h5>
              </div>

              <Row>
                <Col lg={4} className="mb-3">
                  <Form.Label>{t('LABEL_BORDER_RADIUS')}</Form.Label>
                  <div className="number-input-group">
                    <InputGroup>
                      <Form.Control 
                        type="number" 
                        name="search_box.options.border_radius" 
                        value={values.search_box.options.border_radius} 
                        onChange={(e) => setFieldValue('search_box.options.border_radius', Number(e.target.value || 0))} 
                        isInvalid={touched.search_box?.options?.border_radius && !!errors.search_box?.options?.border_radius} 
                      />
                      <InputGroup.Text>px</InputGroup.Text>
                    </InputGroup>
                  </div>
                  <Form.Control.Feedback type="invalid">{touched.search_box?.options?.border_radius && errors.search_box?.options?.border_radius}</Form.Control.Feedback>
                  <Form.Text>{t('TXT_CORNER_RADIUS')}</Form.Text>
                </Col>

                <Col lg={4} className="mb-3">
                  <Form.Label>{t('LABEL_FONT_SIZE')}</Form.Label>
                  <div className="number-input-group">
                    <InputGroup>
                      <Form.Control 
                        type="number" 
                        name="search_box.options.font-size" 
                        value={values.search_box.options['font-size']} 
                        onChange={(e) => setFieldValue('search_box.options["font-size"]', Number(e.target.value || 0))} 
                        isInvalid={touched.search_box?.options && !!errors.search_box?.options?.['font-size']} 
                      />
                      <InputGroup.Text>px</InputGroup.Text>
                    </InputGroup>
                  </div>
                  <Form.Control.Feedback type="invalid">{touched.search_box?.options && errors.search_box?.options?.['font-size']}</Form.Control.Feedback>
                  <Form.Text>{t('TXT_ADJUST_FONT_SIZE')}</Form.Text>
                </Col>

                <Col lg={4} className="mb-3">
                  <Form.Label>{t('LABEL_PADDING')}</Form.Label>
                  <div className="number-input-group">
                    <InputGroup>
                      <Form.Control 
                        type="number" 
                        name="search_box.options.padding" 
                        value={values.search_box.options.padding} 
                        onChange={(e) => setFieldValue('search_box.options.padding', Number(e.target.value || 0))} 
                        isInvalid={touched.search_box?.options?.padding && !!errors.search_box?.options?.padding} 
                      />
                      <InputGroup.Text>px</InputGroup.Text>
                    </InputGroup>
                  </div>
                  <Form.Control.Feedback type="invalid">{touched.search_box?.options?.padding && errors.search_box?.options?.padding}</Form.Control.Feedback>
                  <Form.Text>{t('TXT_INNER_SPACING')}</Form.Text>
                </Col>
              </Row>
            </div>

            {/* Search Button Section */}
            <div className="config-section">
              <div className="section-header">
                <i className="mdi mdi-gesture-tap-button section-icon"></i>
                <h5 className="section-title">{t('LABEL_SEARCH_BUTTON')}</h5>
              </div>

              <Row>
                <Col lg={6} className="mb-3">
                  <Form.Label>{t('LABEL_ICON')}</Form.Label>
                  <Form.Control 
                    type="text" 
                    name="search_button.icon" 
                    value={values.search_button.icon} 
                    onChange={(e) => setFieldValue('search_button.icon', e.target.value)} 
                    placeholder={t('TXT_ICON_PLACEHOLDER')} 
                  />
                  <Form.Text>{t('TXT_ICON_DESC')}</Form.Text>
                </Col>

                <Col lg={6} className="mb-3">
                  <Form.Label>{t('LABEL_BUTTON_BORDER_RADIUS')}</Form.Label>
                  <div className="number-input-group">
                    <InputGroup>
                      <Form.Control 
                        type="number" 
                        name="search_button.border_radius" 
                        value={values.search_button.border_radius} 
                        onChange={(e) => setFieldValue('search_button.border_radius', Number(e.target.value || 0))} 
                      />
                      <InputGroup.Text>px</InputGroup.Text>
                    </InputGroup>
                  </div>
                  <Form.Text>{t('TXT_BUTTON_CORNER_RADIUS')}</Form.Text>
                </Col>

                <Col lg={6} className="mb-3">
                  <Form.Label>{t('LABEL_COLOR')} ({t('LABEL_ICON')})</Form.Label>
                  <div className="color-input-wrapper">
                    <Form.Control 
                      type="color" 
                      name="search_button.color" 
                      value={values.search_button.color} 
                      onChange={(e) => setFieldValue('search_button.color', e.target.value)} 
                    />
                    <div className="color-preview" style={{ backgroundColor: values.search_button.color }}></div>
                  </div>
                  <Form.Text>{t('TXT_BUTTON_ICON_COLOR')}</Form.Text>
                </Col>

                <Col lg={6} className="mb-3">
                  <Form.Label>{t('LABEL_BUTTON_BACKGROUND_COLOR')}</Form.Label>
                  <div className="color-input-wrapper">
                    <Form.Control 
                      type="color" 
                      name="search_button.background_color" 
                      value={values.search_button.background_color} 
                      onChange={(e) => setFieldValue('search_button.background_color', e.target.value)} 
                    />
                    <div className="color-preview" style={{ backgroundColor: values.search_button.background_color }}></div>
                  </div>
                  <Form.Text>{t('TXT_BUTTON_BG_COLOR')}</Form.Text>
                </Col>
              </Row>
            </div>

            {/* Action Buttons Section */}
            <div className="action-buttons">
              <Row>
                <Col lg="7">
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
                <Col lg="5">
                  <div className="d-flex justify-content-end">
                    <Button variant="outline-danger" onClick={() => setShowConfirmResetDefaults(true)} disabled={loading.submitting || showConfirmResetDefaults}>
                      <i className="mdi mdi-backup-restore"></i>
                      <span className="ms-2">{t('BTN_RESET_TO_DEFAULTS')}</span>
                    </Button>
                  </div>
                </Col>
              </Row>
              <Form.Text className="d-block mt-2">{t('TXT_FORM_SUBMIT_CONDITION')}</Form.Text>
            </div>

            {/* Modal for confirming reset to defaults */}
            <Modal show={showConfirmResetDefaults} onHide={() => setShowConfirmResetDefaults(false)} centered>
              <Modal.Header closeButton>
                <Modal.Title>{t('MODAL_TITLE_CONFIRM_RESET_TO_DEFAULTS')}</Modal.Title>
              </Modal.Header>
              <Modal.Body>
                <p>{t('MODAL_TEXT_CONFIRM_RESET_BOX_SEARCH_CONFIG_TO_DEFAULTS')}</p>
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

export default BoxSearchConfigForm;