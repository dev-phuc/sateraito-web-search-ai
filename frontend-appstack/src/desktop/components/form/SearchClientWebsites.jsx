import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

import * as Yup from "yup";
// Library UI imports
import { Formik } from "formik";
import { Form, Button, Spinner, Dropdown } from "react-bootstrap";

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
          <div className="d-flex flex-wrap search-filter-options">
            {/* Site name */}
            {/* <Form.Group className="d-flex align-items-center justify-content-center">
              <Form.Label className="me-2 mb-0 text-nowrap">{t('LABEL_SITE_NAME')}</Form.Label>
              <Form.Control
                type="text"
                name="site_name"
                value={values.site_name}
                onChange={handleChange}
              />
            </Form.Group> */}

            {/* Domain */}
            <Form.Group className="d-flex align-items-center justify-content-center wrap-domain-search">
              {/* <Form.Label className="me-2 mb-0 text-nowrap">{t('LABEL_DOMAIN')}</Form.Label> */}
              <i className="mdi mdi-magnify"></i>
              <Form.Control
                type="text"
                name="domain"
                value={values.domain}
                onChange={handleChange}
                placeholder={t('LABEL_DOMAIN')}
              />
            </Form.Group>

            {/* Status */}
            <Form.Group className="d-flex align-items-center justify-content-center ms-2 me-2">
              <Dropdown className='st-dropdown'>
                <Dropdown.Toggle variant="" className="st-dropdown-toggle  rounded-5">
                  {values.status === '' ? t('LABEL_STATUS') : 
                   values.status === 'active' ? t('STATUS_ACTIVE') : 
                   values.status === 'disabled' ? t('STATUS_DISABLED') : t('LABEL_STATUS')}
                </Dropdown.Toggle>

                <Dropdown.Menu>
                  <Dropdown.Item 
                    active={values.status === ''}
                    onClick={() => setFieldValue('status', '')}
                  >
                    {t('TXT_OPTION_ALL')}
                  </Dropdown.Item>
                  <Dropdown.Item 
                    active={values.status === 'active'}
                    onClick={() => setFieldValue('status', 'active')}
                  >
                    {t('STATUS_ACTIVE')}
                  </Dropdown.Item>
                  <Dropdown.Item 
                    active={values.status === 'disabled'}
                    onClick={() => setFieldValue('status', 'disabled')}
                  >
                    {t('STATUS_DISABLED')}
                  </Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
            </Form.Group>
            {(values.domain || values.site_name || values.status) && (
              <div className="d-flex align-items-center justify-content-center">
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
              <Button
                type="button"
                className="btn st-btn-material-ico ms-2 btn-red"
                variant='red'
                onClick={() => {
                  resetForm();
                  if (onSearch) {
                    onSearch(false);
                  }
                }}
                disabled={isLoading}
              >
              <i className="icon mdi mdi-close"></i>
                </Button>
              </div>
          )}
          </div>
        </Form>
      )}
    </Formik>
  );
};

export default SearchClientWebsitesForm;