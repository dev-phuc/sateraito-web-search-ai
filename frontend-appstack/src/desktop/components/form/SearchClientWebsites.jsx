import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

import * as Yup from "yup";
// Library UI imports
import { Formik } from "formik";
import { Form, Button, Spinner } from "react-bootstrap";

// Hook components

// Requests API

// Zustand

// Constants

const SearchClientWebsitesForm = ({ tenant, app_id, onSearch, isLoading = false }) => {
  // Default hooks
  const navigate = useNavigate();
  const { t } = useTranslation();

  const validationSchema = Yup.object().shape({
    domain: Yup.string(),
    site_name: Yup.string(),
    status: Yup.string(),
  });

  // Constant value
  const initialValues = {
    domain: '',
    site_name: '',
    status: '',
  };

  // Effects
  const handlerOnSubmit = useCallback(async (values) => {
    if (onSearch) {
      onSearch(values);
    }
  }, [onSearch]);

  // Return the component
  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={handlerOnSubmit}
      enableReinitialize
    >
      {({ errors, handleBlur, handleChange, handleSubmit, isSubmitting, touched, values, setFieldValue, resetForm }) => (
        <Form onSubmit={handleSubmit} noValidate className="">
          <div className="d-flex flex-wrap">
            {/* Site name */}
            <Form.Group className="d-flex align-items-center justify-content-center">
              <Form.Label className="me-2 mb-0 text-nowrap">{t('LABEL_SITE_NAME')}</Form.Label>
              <Form.Control
                type="text"
                name="site_name"
                value={values.site_name}
                onChange={handleChange}
              />
            </Form.Group>

            {/* Domain */}
            <Form.Group className="d-flex align-items-center justify-content-center ms-2">
              <Form.Label className="me-2 mb-0 text-nowrap">{t('LABEL_DOMAIN')}</Form.Label>
              <Form.Control
                type="text"
                name="domain"
                value={values.domain}
                onChange={handleChange}
              />
            </Form.Group>

            {/* Status */}
            <Form.Group className="d-flex align-items-center justify-content-center ms-2 me-2">
              <Form.Label className="me-2 mb-0 text-nowrap">{t('LABEL_STATUS')}</Form.Label>
              <Form.Select
                name="status"
                value={values.status}
                onChange={handleChange}
              >
                <option value="">{t('TXT_OPTION_ALL')}</option>
                <option value="active">{t('STATUS_ACTIVE')}</option>
                <option value="disabled">{t('STATUS_DISABLED')}</option>
              </Form.Select>
            </Form.Group>

            {/* Button submit */}
            <Button type="submit" className="btn btn-primary ms-2" disabled={isLoading}>
              {isLoading ? (
                <Spinner as="span" animation="border" role="status" aria-hidden="true" />
              ) : (
                <div>
                  <span className="icon mdi mdi-filter me-2"></span>
                  <span className="text">
                    {t('BTN_FILTER')}
                  </span>
                </div>
              )}
            </Button>

            {/* Clear form */}
            {(values.domain || values.site_name || values.status) && (
              <Button
                type="button"
                className="btn btn-secondary ms-2"
                onClick={() => {
                  resetForm();
                  if (onSearch) {
                    onSearch(false);
                  }
                }}
                disabled={isLoading}
              >
                <div>
                  <span className="text">
                    {t('BTN_CLEAR')}
                  </span>
                </div>
              </Button>
            )}
          </div>
        </Form>
      )}
    </Formik>
  );
};

export default SearchClientWebsitesForm;