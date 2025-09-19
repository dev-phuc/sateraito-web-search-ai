import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

import * as Yup from "yup";
// Library UI imports
import { Formik } from "formik";
import { Form, Button, InputGroup, FormControl } from "react-bootstrap";

// Hook components
import useTheme from '@/hooks/useTheme'

// Requests API

// Zustand
import useStoreTenantConfig from '@/store/tenant_config';

// Constants

// Utils
import { isTelephoneNumber } from '@/utils';

const ContractInformationForm = ({ tenant, app_id, onCancel, afterSubmit }) => {
  // Default hooks
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { showNotice } = useTheme();

  // Zustand stores
  const { contractInformation, updateContractInfo } = useStoreTenantConfig();

  const validationSchema = Yup.object().shape({
    mail_address: Yup.string()
      .email(t('MSG_ERROR_INVALID_EMAIL'))
      .nullable(),
    tel_no: Yup.string()
      .test('is-valid-tel', t('invalid_tel_no'), value => {
        if (!value) return true;
        return isTelephoneNumber(value);
      }).nullable(),
  });

  const [loading, setLoading] = useState({
    submitting: false,
  });

  // Constant value
  const initialValues = {
    mail_address: contractInformation?.mail_address || '',
    tel_no: contractInformation?.tel_no || '',
  };

  const handlerOnSubmit = async (values) => {
    if (loading.submitting) return;
    setLoading(temp => ({ ...temp, submitting: true }));

    const { success, message } = await updateContractInfo(tenant, app_id, values);
    if (success) {
      showNotice('success', t('TXT_UPDATE_SUCCESS'));
      if (afterSubmit) {
        afterSubmit(success);
      }
    } else {
      let displayMessage = t(message);
      if (displayMessage === message) {
        displayMessage = t('TXT_ERROR_UPDATE_FAILED');
      }
      showNotice('error', displayMessage);
    }

    setLoading(temp => ({ ...temp, submitting: false }));
  };

  // Return the component
  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={handlerOnSubmit}
    >
      {({ errors, handleBlur, handleChange, handleSubmit, isSubmitting, touched, values, setFieldValue }) => (
        <Form onSubmit={handleSubmit} className="w-100 pb-2">
          {/* Email Address Field */}
          <Form.Group className="mb-3">
            <Form.Label>{t('LABEL_MAIL_ADDRESS')}</Form.Label>
            <FormControl
              type="email"
              name="mail_address"
              value={values.mail_address || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              disabled={loading.submitting}
              placeholder={t('PLACEHOLDER_MAIL_ADDRESS')}
              isInvalid={touched.mail_address && !!errors.mail_address}
            />
            {touched.mail_address && errors.mail_address && (
              <Form.Control.Feedback type="invalid" style={{ display: 'block' }}>
                {errors.mail_address}
              </Form.Control.Feedback>
            )}
          </Form.Group>

          {/* Telephone Number Field */}
          <Form.Group className="mb-3">
            <Form.Label>{t('LABEL_TEL_NO')}</Form.Label>
            <FormControl
              type="text"
              name="tel_no"
              value={values.tel_no || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              disabled={loading.submitting}
              placeholder={t('PLACEHOLDER_TEL_NO')}
              isInvalid={touched.tel_no && !!errors.tel_no}
            />
            {touched.tel_no && errors.tel_no && (
              <Form.Control.Feedback type="invalid" style={{ display: 'block' }}>
                {errors.tel_no}
              </Form.Control.Feedback>
            )}
          </Form.Group>

          {/* Submit Buttons */}
          <div className="d-flex justify-content-end gap-2">
            <Button
              variant="outline-secondary"
              disabled={loading.submitting}
              onClick={() => onCancel && onCancel()}
            >
              <i className="mdi mdi-close me-1"></i>
              {t('BTN_CANCEL')}
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={loading.submitting}
            >
              <i className={`mdi mdi-content-save me-1`}></i>
              {loading.submitting ? t('TXT_LOADING') + '...' : t('BTN_UPDATE')}
            </Button>
          </div>
        </Form>
      )}
    </Formik>
  );
};

export default ContractInformationForm;