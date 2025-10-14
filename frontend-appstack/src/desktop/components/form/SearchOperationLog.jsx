import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

import * as Yup from "yup";
// Library UI imports
import { Formik } from "formik";
import { Form, Button, Spinner, Dropdown } from "react-bootstrap";

// Hook components
import useTheme from "@/hooks/useTheme";

// Requests API

// Zustand
import useStoreClientWebsites from '@/store/client_websites';

// Constants

const SearchOperationLogForm = ({ tenant, app_id, onSearch, isLoading = false }) => {
  // Default hooks
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { showNotice } = useTheme();

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

  // Handlers
  const handlerLoadClientWebsites = async () => {
    if (tenant && app_id) {
      const { success, message } = await fetchClientWebsites(tenant, app_id);
      if (!success) {
        showNotice("danger", t(message));
      }
    }
  };

  // Effects
  useEffect(() => {
    handlerLoadClientWebsites();
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
          <div className="d-flex search-filter-options">
            {/* Select client website */}
            <Form.Group className="d-flex align-items-center justify-content-center me-2">
              <Dropdown className='st-dropdown'>
                <Dropdown.Toggle variant="" className="st-dropdown-toggle rounded-5">
                  <span className="mdi mdi-web"></span>
                  {values.client_domain === '' ? t('LABEL_DOMAIN') : values.client_domain}
                </Dropdown.Toggle>

                <Dropdown.Menu>
                  <Dropdown.Item 
                    active={values.client_domain === ''}
                    onClick={() => setFieldValue('client_domain', '')}
                  >
                    {t('TXT_OPTION_ALL')}
                  </Dropdown.Item>
                  {clientWebsites.map((website) => (
                    <Dropdown.Item 
                      key={website.id}
                      active={values.client_domain === website.domain}
                      onClick={() => setFieldValue('client_domain', website.domain)}
                    >
                      {website.domain}
                    </Dropdown.Item>
                  ))}
                </Dropdown.Menu>
              </Dropdown>
            </Form.Group>

            {/* Date picker from */}
            <Form.Group className="d-flex align-items-center justify-content-center ms-2">
              <div className="st-date-input-wrapper position-relative">
                <Form.Control
                  type="date"
                  name="from_date"
                  value={values.from_date}
                  onChange={handleChange}
                  className="st-dropdown-toggle "
                  style={{ color: values.from_date ? '#000' : 'transparent' }}
                />
                {!values.from_date && (
                  <span className="st-date-placeholder position-absolute top-50 start-0 translate-middle-y ps-3">
                    {t('LABEL_FROM_DATE')}
                    {/* <i className="mdi mdi-calendar me-2"></i> */}
                  </span>
                )}
              </div>
            </Form.Group>
            <div className="d-flex align-items-center justify-content-center mx-2">
              <i className="mdi mdi-arrow-right text-muted"></i>
            </div>
            {/* Date picker to */}
            <Form.Group className="d-flex align-items-center justify-content-center me-2">
              <div className="st-date-input-wrapper position-relative">
                <Form.Control
                  type="date"
                  name="to_date"
                  value={values.to_date}
                  onChange={handleChange}
                  className="st-dropdown-toggle "
                  style={{ color: values.to_date ? '#000' : 'transparent' }}
                />
                {!values.to_date && (
                  <span className="st-date-placeholder position-absolute top-50 start-0 translate-middle-y ps-3">
                    {t('LABEL_TO_DATE')}
                    {/* <i className="mdi mdi-calendar me-2"></i> */}
                  </span>
                )}
              </div>
            </Form.Group>

            {/* Button submit */}
            <Button type="submit" className="btn st-btn-material ms-2" disabled={isLoading}>
              {isLoading ? (
                <Spinner as="span" animation="border" role="status" aria-hidden="true" />
              ) : (
                <div className='d-f-c'>
                  <i className="icon mdi mdi-filter me-2"></i>
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
                className="btn st-btn-material-ico ms-2 btn-red"
                variant='red'
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
                <i className="icon mdi mdi-close"></i>
              </Button>
            )}
          </div>
        </Form>
      )}
    </Formik>
  );
};

export default SearchOperationLogForm;