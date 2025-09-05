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
import { getPageInfoByUrl } from '@/request/sateraitoUtils';

// Zustand
import useStoreApp from '@/store/app';
import useStoreClientWebsites from '@/store/client_websites';

// Constants
import { STATUS_CLIENT_WEBSITES_ACTIVE, STATUS_CLIENT_WEBSITES_DISABLED } from '@/constants';

const ClientWebsitesForm = ({ tenant, app_id, data, onCancel, afterSubmit }) => {
  // Default hooks
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { showNotice } = useTheme();

  // Zustand stores
  const { createClientWebsites, editClientWebsites } = useStoreClientWebsites();

  const validationSchema = Yup.object().shape({
    domain: Yup.string()
      .matches(
        /^(https?:\/\/)?([\w-]+(\.[\w-]+)+)(\/[\w-./?%&=]*)?$/,
        t('MSG_ERROR_DOMAIN_INVALID')
      )
      .required(t('MSG_ERROR_DOMAIN_REQUIRED')),
    site_name: Yup.string().max(255),
    description: Yup.string().max(1000),
    status: Yup.string().required(t('MSG_ERROR_STATUS_REQUIRED'))
  });

  const [isEdit] = useState(!!data);
  const [loading, setLoading] = useState({
    submitting: false,
    fetchingPageInfo: false,
  });
  const [faviconUrl, setFaviconUrl] = useState(data?.favicon_url || null);
  const [pageInfoCache, setPageInfoCache] = useState({});

  // Constant value
  const initialValues = {
    domain: data?.domain || '',
    favicon_url: data?.favicon_url || '',
    site_name: data?.site_name || '',
    description: data?.description || '',
    ai_enabled: data?.ai_enabled ?? true,
    status: data?.status || STATUS_CLIENT_WEBSITES_ACTIVE,
  };
  if (isEdit && data?.id) {
    initialValues.id = data.id;
  }

  const handleDomainBlur = useCallback(async (e, setFieldValue) => {
    const url = e.target.value;
    if (!url) return;

    if (pageInfoCache[url]) {
      const pageInfo = pageInfoCache[url];
      setFieldValue('favicon_url', pageInfo.favicon_url || '');
      setFieldValue('site_name', pageInfo.site_name || '');
      setFieldValue('description', pageInfo.description || '');
      setFaviconUrl(pageInfo.favicon_url || '');
      return;
    }

    setLoading(l => ({ ...l, fetchingPageInfo: true }));
    try {
      const pageInfo = await getPageInfoByUrl(url);
      if (pageInfo) {
        setFieldValue('favicon_url', pageInfo.favicon_url || '');
        setFieldValue('site_name', pageInfo.site_name || '');
        setFieldValue('description', pageInfo.description || '');
        setFaviconUrl(pageInfo.favicon_url || '');
        setPageInfoCache(prev => ({ ...prev, [url]: pageInfo }));
      }
    } catch (error) {
      let message = error?.response?.data?.message;
      if (message === 'failed_to_fetch_page') {
        message = 'MSG_WARNING_FETCH_PAGE_INFO';
      }
      showNotice('warning', t(message));
    } finally {
      setLoading(l => ({ ...l, fetchingPageInfo: false }));
    }
  }, [tenant, app_id, pageInfoCache]);

  const handlerOnSubmit = useCallback(async (values) => {
    if (loading.submitting) return;
    setLoading(l => ({ ...l, submitting: true }));

    let result;
    if (isEdit) {
      result = await editClientWebsites(tenant, app_id, data.id, values);
    } else {
      result = await createClientWebsites(tenant, app_id, values);
    }

    const { success, error } = result;
    let message = '';
    if (success) {
      message = isEdit ? t('TXT_UPDATE_CLIENT_WEBSITES_SUCCESS') : t('TXT_CREATE_CLIENT_WEBSITES_SUCCESS');
      showNotice('success', message);

      if (afterSubmit) {
        afterSubmit(success);
      }
    } else {
      message = t(error);
      if (message === error) {
        message = isEdit ? t('TXT_ERROR_UPDATE_CLIENT_WEBSITES') : t('TXT_ERROR_CREATE_CLIENT_WEBSITES');
      }
      showNotice('error', message);
    }

    setLoading(l => ({ ...l, submitting: false }));

  }, [loading.submitting, createClientWebsites, editClientWebsites, tenant, app_id, data?.id, isEdit, t, afterSubmit]);

  // Return the component
  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={handlerOnSubmit}
    >
      {({ errors, handleBlur, handleChange, handleSubmit, isSubmitting, touched, values, setFieldValue }) => (
        <Form onSubmit={handleSubmit} className="w-100 pb-2">
          {/* Avatar/Favicon Display */}
          <div className="text-center mb-3">
            {faviconUrl ? (
              <img
                src={faviconUrl}
                alt="Favicon"
                style={{ width: 64, height: 64, borderRadius: '50%', objectFit: 'cover' }}
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'flex';
                }}
              />
            ) : null}
            <div
              className={`d-flex align-items-center justify-content-center ${faviconUrl ? 'd-none' : ''}`}
              style={{
                width: 64,
                height: 64,
                borderRadius: '50%',
                backgroundColor: '#f0f0f0',
                margin: '0 auto',
                color: '#999'
              }}
            >
              <i className="mdi mdi-web" style={{ fontSize: '1.5rem' }}></i>
            </div>
          </div>

          {/* Domain Field */}
          <Form.Group className="mb-3">
            <Form.Label>{t('LABEL_DOMAIN')}</Form.Label>
            <InputGroup>
              <FormControl
                type="text"
                name="domain"
                value={values.domain || ''}
                onChange={handleChange}
                onBlur={(e) => {
                  handleBlur(e);
                  handleDomainBlur(e, setFieldValue);
                }}
                disabled={isEdit || loading.fetchingPageInfo || loading.submitting}
                placeholder={t('PLACEHOLDER_CLIENT_WEBSITES_DOMAIN')}
                isInvalid={touched.domain && !!errors.domain}
              />
              {loading.fetchingPageInfo && (
                <InputGroup.Text>
                  <small className="text-muted">{t('TXT_LOADING')}...</small>
                </InputGroup.Text>
              )}
            </InputGroup>
            {touched.domain && errors.domain && (
              <Form.Control.Feedback type="invalid" style={{ display: 'block' }}>
                {errors.domain}
              </Form.Control.Feedback>
            )}
          </Form.Group>

          {/* Favicon URL Field */}
          <Form.Group className="mb-3">
            <Form.Label>{t('LABEL_FAVICON_URL')}</Form.Label>
            <FormControl
              type="text"
              name="favicon_url"
              value={values.favicon_url || ''}
              onChange={(e) => {
                handleChange(e);
                setFaviconUrl(e.target.value);
              }}
              onBlur={handleBlur}
              disabled={loading.fetchingPageInfo || loading.submitting}
              placeholder={t('PLACEHOLDER_CLIENT_WEBSITES_FAVICON_URL')}
            />
          </Form.Group>

          {/* Site Name Field */}
          <Form.Group className="mb-3">
            <Form.Label>{t('LABEL_SITE_NAME')}</Form.Label>
            <FormControl
              type="text"
              name="site_name"
              value={values.site_name || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              disabled={loading.fetchingPageInfo || loading.submitting}
              placeholder={t('PLACEHOLDER_CLIENT_WEBSITES_SITE_NAME')}
            />
          </Form.Group>

          {/* Description Field */}
          <Form.Group className="mb-3">
            <Form.Label>{t('LABEL_DESCRIPTION')}</Form.Label>
            <FormControl
              as="textarea"
              rows={3}
              name="description"
              value={values.description || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              disabled={loading.fetchingPageInfo || loading.submitting}
              placeholder={t('PLACEHOLDER_CLIENT_WEBSITES_DESCRIPTION')}
            />
          </Form.Group>

          {/* AI Enabled Field */}
          <Form.Group className="mb-3">
            <Form.Check
              type="switch"
              id="ai_enabled"
              name="ai_enabled"
              label={t('LABEL_AI_ENABLED')}
              checked={values.ai_enabled}
              onChange={handleChange}
              disabled={loading.fetchingPageInfo || loading.submitting}
            />
          </Form.Group>

          {/* Status Field */}
          <Form.Group className="mb-3">
            <Form.Label>{t('LABEL_STATUS')}</Form.Label>
            <Form.Select
              name="status"
              value={values.status || STATUS_CLIENT_WEBSITES_ACTIVE}
              onChange={handleChange}
              onBlur={handleBlur}
              disabled={loading.fetchingPageInfo || loading.submitting}
              isInvalid={touched.status && !!errors.status}
            >
              {[STATUS_CLIENT_WEBSITES_ACTIVE, STATUS_CLIENT_WEBSITES_DISABLED].map(status => (
                <option key={status} value={status}>
                  {t(`STATUS_${status.toUpperCase()}`)}
                </option>
              ))}
            </Form.Select>
            {touched.status && errors.status && (
              <Form.Control.Feedback type="invalid" style={{ display: 'block' }}>
                {errors.status}
              </Form.Control.Feedback>
            )}
          </Form.Group>

          {/* Submit Buttons */}
          <div className="d-flex justify-content-end gap-2">
            <Button
              variant="outline-secondary"
              disabled={loading.submitting || loading.fetchingPageInfo}
              onClick={() => onCancel && onCancel()}
            >
              <i className="mdi mdi-close me-1"></i>
              {t('BTN_CANCEL')}
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={loading.fetchingPageInfo || loading.submitting}
            >
              <i className={`mdi ${isEdit ? 'mdi-pencil' : 'mdi-plus'} me-1`}></i>
              {loading.submitting ? t('TXT_LOADING') + '...' : (isEdit ? t('BTN_UPDATE') : t('BTN_CREATE'))}
            </Button>
          </div>
        </Form>
      )}
    </Formik>
  );
};

export default ClientWebsitesForm;