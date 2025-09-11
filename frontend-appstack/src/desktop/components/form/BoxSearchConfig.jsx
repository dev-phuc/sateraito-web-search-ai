import { useState, useEffect, useCallback, useRef } from 'react';
import { useTranslation } from 'react-i18next';

import * as Yup from "yup";
// Library UI imports
import { Formik } from "formik";
import { Form, Button, InputGroup, FormControl, Spinner, Row, Col, Card } from "react-bootstrap";

// Hook components
import useTheme from '@/hooks/useTheme'

// Zustand
import useStoreBoxSearchConfig from '@/store/box_search_config';

// Constants
import { BOX_SEARCH_DESIGN_DEFAULT } from '@/constants';

const BoxSearchConfigForm = ({ tenant, app_id, data, onCancel, afterSubmit }) => {
  // Default hooks
  const { t } = useTranslation();
  const { showNotice } = useTheme();

  // State
  const [loading, setLoading] = useState({ submitting: false });
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

  if (!boxSearchConfig) {
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
        
        useEffect(() => {
          handlerOnChange(values);
        }, [values]);

        return (
          <Form onSubmit={handleSubmit} noValidate className=''>
            {/* Search Box Section */}
            <Card className='p-3 mx-2 mt-2 mb-3'>
              <Card.Title>{t('LABEL_SEARCH_BOX')}</Card.Title>

              <Form.Group className="mb-3">
                <Form.Label>{t('LABEL_TYPE')}</Form.Label>
                <div className="d-flex flex-wrap">
                  <Form.Check
                    type="radio"
                    id="search_box_type_box"
                    name="search_box.type"
                    label={t('LABEL_BOX')}
                    value="box"
                    checked={values.search_box.type === "box"}
                    onChange={() => setFieldValue('search_box.type', 'box')}
                    isInvalid={touched.search_box?.type && !!errors.search_box?.type}
                    inline
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
                    inline
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
                    inline
                  />
                </div>
                <Form.Control.Feedback type="invalid">{touched.search_box?.type && errors.search_box?.type}</Form.Control.Feedback>
                <Form.Text className="text-muted">{t('TXT_CHOOSE_SEARCH_UI')}</Form.Text>
              </Form.Group>

              <h6>{t('LABEL_OPTIONS')}</h6>

              <Row>
                
                <Col md={2} className="mb-3">
                  <Form.Label>{t('LABEL_COLOR')}</Form.Label>
                  <Form.Control type="color" name="theme.color" value={values.theme.color} onChange={(e) => setFieldValue('theme.color', e.target.value)} />
                </Col>

                <Col md={3} className="mb-3">
                  <Form.Label>{t('LABEL_BACKGROUND_COLOR')}</Form.Label>
                  <Form.Control type="color" name="search_box.options.background_color" value={values.search_box.options.background_color} onChange={(e) => setFieldValue('search_box.options.background_color', e.target.value)} isInvalid={touched.search_box?.options?.background_color && !!errors.search_box?.options?.background_color} />
                  <Form.Control.Feedback type="invalid">{touched.search_box?.options?.background_color && errors.search_box?.options?.background_color}</Form.Control.Feedback>
                  {/* <Form.Text className="text-muted small">{t('TXT_PICK_BACKGROUND_COLOR')}</Form.Text> */}
                </Col>

                <Col md={7} className="mb-3 align-items-center">
                  <div className='w-100'>
                    <label>{t('LABEL_SHADOW')}</label>
                    <Form.Check className="me-3" type="switch" name="search_box.options.shadow" checked={values.search_box.options.shadow} onChange={(e) => setFieldValue('search_box.options.shadow', e.target.checked)} />
                  </div>
                  <Form.Text className="text-muted small mb-0">{t('TXT_ENABLE_SHADOW')}</Form.Text>
                </Col>
              </Row>

              <Row>

                <Col md={12} className="mb-3">
                  <Form.Label>{t('LABEL_FONT')}</Form.Label>
                  <Form.Control type="text" name="theme.font" value={values.theme.font} onChange={(e) => setFieldValue('theme.font', e.target.value)} placeholder={t('TXT_FONT_PLACEHOLDER')} />
                  {/* <Form.Text className="text-muted small">{t('TXT_FONT_DESC')}</Form.Text> */}
                </Col>

                <Col md={4} className="mb-3">
                  <Form.Label>{t('LABEL_BORDER_RADIUS')}</Form.Label>
                  <InputGroup>
                    <Form.Control type="number" name="search_box.options.border_radius" value={values.search_box.options.border_radius} onChange={(e) => setFieldValue('search_box.options.border_radius', Number(e.target.value || 0))} isInvalid={touched.search_box?.options?.border_radius && !!errors.search_box?.options?.border_radius} />
                    <InputGroup.Text>px</InputGroup.Text>
                  </InputGroup>
                  <Form.Control.Feedback type="invalid">{touched.search_box?.options?.border_radius && errors.search_box?.options?.border_radius}</Form.Control.Feedback>
                  <Form.Text className="text-muted small">{t('TXT_CORNER_RADIUS')}</Form.Text>
                </Col>

                <Col md={4} className="mb-3">
                  <Form.Label>{t('LABEL_FONT_SIZE')}</Form.Label>
                  <InputGroup>
                    <Form.Control type="number" name="search_box.options.font-size" value={values.search_box.options['font-size']} onChange={(e) => setFieldValue('search_box.options["font-size"]', Number(e.target.value || 0))} isInvalid={touched.search_box?.options && !!errors.search_box?.options?.['font-size']} />
                    <InputGroup.Text>px</InputGroup.Text>
                  </InputGroup>
                  <Form.Control.Feedback type="invalid">{touched.search_box?.options && errors.search_box?.options?.['font-size']}</Form.Control.Feedback>
                  <Form.Text className="text-muted small">{t('TXT_ADJUST_FONT_SIZE')}</Form.Text>
                </Col>

                <Col md={4} className="mb-3">
                  <Form.Label>{t('LABEL_PADDING')}</Form.Label>
                  <InputGroup>
                    <Form.Control type="number" name="search_box.options.padding" value={values.search_box.options.padding} onChange={(e) => setFieldValue('search_box.options.padding', Number(e.target.value || 0))} isInvalid={touched.search_box?.options?.padding && !!errors.search_box?.options?.padding} />
                    <InputGroup.Text>px</InputGroup.Text>
                  </InputGroup>
                  <Form.Control.Feedback type="invalid">{touched.search_box?.options?.padding && errors.search_box?.options?.padding}</Form.Control.Feedback>
                  <Form.Text className="text-muted small">{t('TXT_INNER_SPACING')}</Form.Text>
                </Col>

              </Row>
            </Card>

            {/* Search Button Section */}
            <Card className='p-3 mx-2 mt-2 mb-3'>
              <Card.Title>{t('LABEL_SEARCH_BUTTON')}</Card.Title>

              <Row>
                <Col md={6} className="mb-3">
                  <Form.Group className="mb-3">
                    <Form.Label>{t('LABEL_ICON')}</Form.Label>
                    <Form.Control type="text" name="search_button.icon" value={values.search_button.icon} onChange={(e) => setFieldValue('search_button.icon', e.target.value)} placeholder={t('TXT_ICON_PLACEHOLDER')} />
                    <Form.Text className="text-muted small">{t('TXT_ICON_DESC')}</Form.Text>
                  </Form.Group>
                </Col>

                <Col md={6} className="mb-3">
                  <Form.Group className="mb-3">
                    <Form.Label>{t('LABEL_BUTTON_BORDER_RADIUS')}</Form.Label>
                    <InputGroup>
                      <Form.Control type="number" name="search_button.border_radius" value={values.search_button.border_radius} onChange={(e) => setFieldValue('search_button.border_radius', Number(e.target.value || 0))} />
                      <InputGroup.Text>px</InputGroup.Text>
                    </InputGroup>
                    <Form.Text className="text-muted small">{t('TXT_BUTTON_CORNER_RADIUS')}</Form.Text>
                  </Form.Group>
                </Col>
                <Col md={2} className="mb-3">
                  <Form.Label>{t('LABEL_COLOR')}</Form.Label>
                  <Form.Control type="color" name="search_button.color" value={values.search_button.color} onChange={(e) => setFieldValue('search_button.color', e.target.value)} />
                </Col>
                <Col md={6} className="mb-3">
                  <Form.Label>{t('LABEL_BUTTON_BACKGROUND_COLOR')}</Form.Label>
                  <Form.Control type="color" name="search_button.background_color" value={values.search_button.background_color} onChange={(e) => setFieldValue('search_button.background_color', e.target.value)} />
                </Col>
              </Row>
            </Card>

            <div className='px-3 mx-2 mb-3'>
              <Row className="mt-3">
                <Col md="8">
                  <Button type="submit" disabled={loading.submitting || !isValid || (!dirty && !isSubmitting)} aria-busy={loading.submitting}>
                    {loading.submitting ? (<><Spinner animation="border" size="sm" /> <span className="ms-2">{t('TXT_LOADING')}</span></>) : t('BTN_SUBMIT')}
                  </Button>
                  {onCancel && <Button variant="secondary" onClick={onCancel} className="ms-2">{t('BTN_CANCEL')}</Button>}
                  <Button variant="outline-secondary" onClick={() => resetForm()} className="ms-2">{t('BTN_RESET')}</Button>
                </Col>
                <Col md="4">
                  <div className="d-flex justify-content-end">
                    <Button variant="outline-danger" onClick={() => resetForm({ values: BOX_SEARCH_DESIGN_DEFAULT })}>{t('BTN_RESET_TO_DEFAULTS')}</Button>
                  </div>
                </Col>
                <Form.Text className="d-block text-muted mt-2">{t('TXT_FORM_SUBMIT_CONDITION')}</Form.Text>
              </Row>
            </div>

          </Form>
        )
      }}
    </Formik>
  );
};

export default BoxSearchConfigForm;