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
import useStoreClientWebsites from '@/store/client_websites';

// Constants

const SearchOperationLogForm = ({ tenant, app_id, onSearch, isLoading = false }) => {
  // Default hooks
  const navigate = useNavigate();
  const { t } = useTranslation();

  // Zustand stores
  const { clientWebsites, fetchClientWebsites } = useStoreClientWebsites();

  const validationSchema = Yup.object().shape({
    client_domain: Yup.string(),
    from_date: Yup.string(),
    to_date: Yup.string(),
  });

  // Constant value
  const initialValues = {
    client_domain: '',
    from_date: '',
    to_date: '',
  };

  // Effects
  useEffect(() => {
    if (clientWebsites.length === 0 && tenant && app_id) {
      fetchClientWebsites(tenant, app_id);
    }
  }, [tenant, app_id]);

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
          <div className="d-flex">
            {/* Select client website */}
            <Form.Group className="d-flex align-items-center justify-content-center">
              <Form.Label className="me-2 mb-0 text-nowrap">{t('LABEL_DOMAIN')}</Form.Label>
              <Form.Select
                aria-label={t('PLACEHOLDER_SELECT_CLIENT_WEBSITE')}
                name="client_domain"
                value={values.client_domain}
                onChange={(e) => {
                  const selectedId = e.target.value;
                  setFieldValue('client_domain', selectedId);
                }}
                className="me-2"
              >
                <option value="">{t('TXT_OPTION_ALL')}</option>
                {clientWebsites.map((website) => (
                  <option key={website.id} value={website.domain}>{website.domain}</option>
                ))}
              </Form.Select>
            </Form.Group>

            {/* Date picker from */}
            <Form.Group className="d-flex align-items-center justify-content-center ms-2">
              <Form.Label className="me-2 mb-0 text-nowrap">{t('LABEL_FROM_DATE')}</Form.Label>
              <Form.Control
                type="date"
                name="from_date"
                value={values.from_date}
                onChange={handleChange}
              />
            </Form.Group>

            {/* Date picker to */}
            <Form.Group className="d-flex align-items-center justify-content-center ms-2 me-2">
              <Form.Label className="me-2 mb-0 text-nowrap">{t('LABEL_TO_DATE')}</Form.Label>
              <Form.Control
                type="date"
                name="to_date"
                value={values.to_date}
                onChange={handleChange}
              />
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
            {(values.client_domain || values.from_date || values.to_date) && (
              <Button
                type="button"
                className="btn btn-secondary ms-2"
                onClick={() => {
                  resetForm();
                  if (onSearch) {
                    onSearch({
                      client_domain: '',
                      from_date: '',
                      to_date: '',
                    });
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

export default SearchOperationLogForm;