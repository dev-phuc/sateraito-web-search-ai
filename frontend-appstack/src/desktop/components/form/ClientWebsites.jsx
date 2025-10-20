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
import useStoreClientWebsites from '@/store/client_websites';

// Utils
import { removeTrailingSlash } from '@/utils';
import style from './Style.scss';

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
        /^(https?:\/\/)?([\w-]+(\.[\w-]+)+)(:[0-9]{1,5})?(\/.*)?$/,
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

    setLoading(temp => ({ ...temp, fetchingPageInfo: true }));
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
      setLoading(temp => ({ ...temp, fetchingPageInfo: false }));
    }
  }, [tenant, app_id, pageInfoCache]);

  const handlerOnSubmit = useCallback(async (values) => {
    if (loading.submitting) return;
    setLoading(temp => ({ ...temp, submitting: true }));

    let result;
    if (isEdit) {
      result = await editClientWebsites(tenant, app_id, data.id, values);
    } else {
      result = await createClientWebsites(tenant, app_id, values);
    }

    const { success, message } = result;
    if (success) {
      let messageNotice = isEdit ? t('TXT_UPDATE_CLIENT_WEBSITES_SUCCESS') : t('TXT_CREATE_CLIENT_WEBSITES_SUCCESS');
      showNotice('success', messageNotice);

      if (afterSubmit) {
        afterSubmit(success);
      }
    } else {
      let messageNotice = t(message);
      if (messageNotice === message) {
        messageNotice = isEdit ? t('TXT_ERROR_UPDATE_CLIENT_WEBSITES') : t('TXT_ERROR_CREATE_CLIENT_WEBSITES');
      }
      showNotice('error', messageNotice);
    }

    setLoading(temp => ({ ...temp, submitting: false }));

  }, [loading.submitting, createClientWebsites, editClientWebsites, tenant, app_id, data?.id, isEdit, t, afterSubmit]);

  // Return the component
  return (
    <div className="modern-form-container">


      <Formik
        initialValues={initialValues}
        validationSchema={validationSchema}
        onSubmit={handlerOnSubmit}
      >
        {({ errors, handleBlur, handleChange, handleSubmit, isSubmitting, touched, values, setFieldValue }) => (
          <Form onSubmit={handleSubmit} className="client-website-form"
>
            {/* Header */}
            <div className="form-header">
              <div className="favicon-display">
                {faviconUrl ? (
                  <img
                    src={faviconUrl}
                    alt="Favicon"
                    className="favicon-image"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'flex';
                    }}
                  />
                ) : null}
                <div
                  className={`favicon-placeholder ${faviconUrl ? 'd-none' : 'd-flex'} align-items-center justify-content-center w-100 h-100`}
                >
                  <i className="mdi mdi-web"></i>
                </div>
              </div>
              <h3 className="form-title">
                {isEdit ? t('BTN_UPDATE') : t('BTN_CREATE')} Website
              </h3>
              <p className="form-subtitle">
                {isEdit ? 'Update website information' : 'Add a new website to your collection'}
              </p>
            </div>

            {/* Domain Field */}
            <div className="modern-form-group">
              <label className="modern-form-label">{t('LABEL_DOMAIN')}</label>
              <div className="domain-input-container">
                <i className="mdi mdi-web domain-input-icon"></i>
                <input
                  type="text"
                  name="domain"
                  className={`modern-form-control domain-input ${touched.domain && errors.domain ? 'input-error' : ''}`}
                  value={values.domain || ''}
                  onChange={handleChange}
                  onBlur={(e) => {
                    handleBlur(e);
                    handleDomainBlur(e, setFieldValue);
                  }}
                  disabled={isEdit || loading.fetchingPageInfo || loading.submitting}
                  placeholder="https://example.com"
                />
              </div>
              {loading.fetchingPageInfo && (
                <div className="loading-indicator">
                  <div className="loading-spinner"></div>
                  <span>{t('TXT_FETCHING_PAGE_INFO')}...</span>
                </div>
              )}
              {touched.domain && errors.domain && (
                <div className="error-message">
                  <i className="mdi mdi-alert-circle-outline"></i>
                  {errors.domain}
                </div>
              )}
            </div>

            {/* Site Name Field */}
            <div className="modern-form-group">
              <label className="modern-form-label">{t('LABEL_SITE_NAME')}</label>
              <input
                type="text"
                name="site_name"
                className="modern-form-control"
                value={values.site_name || ''}
                onChange={handleChange}
                onBlur={handleBlur}
                disabled={loading.fetchingPageInfo || loading.submitting}
                placeholder="Website Name"
              />
            </div>

            {/* Description Field */}
            <div className="modern-form-group">
              <label className="modern-form-label">{t('LABEL_DESCRIPTION')}</label>
              <textarea
                name="description"
                className="modern-form-control modern-textarea"
                value={values.description || ''}
                onChange={handleChange}
                onBlur={handleBlur}
                disabled={loading.fetchingPageInfo || loading.submitting}
                placeholder="Brief description of the website..."
                rows={3}
              />
            </div>

            {/* Favicon URL Field */}
            <div className="modern-form-group">
              <label className="modern-form-label">{t('LABEL_FAVICON_URL')}</label>
              <input
                type="text"
                name="favicon_url"
                className="modern-form-control"
                value={values.favicon_url || ''}
                onChange={(e) => {
                  handleChange(e);
                  setFaviconUrl(e.target.value);
                }}
                onBlur={handleBlur}
                disabled={loading.fetchingPageInfo || loading.submitting}
                placeholder="https://example.com/favicon.ico"
              />
            </div>

            {/* AI Enabled & Status Fields */}
            <div className="state-website-form d-flex gap-3">
              {/* AI Enabled Field */}
              <div className="modern-form-group mb-0">
                <label className="modern-form-label mb-2">{t('LABEL_AI_ENABLED')}</label>
                <div className="modern-switch-container py-2">
                  <span className="modern-switch-label me-3">{values.ai_enabled ? 'Enabled' : 'Disabled'}</span>
                  <div
                    className={`modern-switch ${values.ai_enabled ? 'active' : ''}`}
                    onClick={() => !loading.fetchingPageInfo && !loading.submitting && setFieldValue('ai_enabled', !values.ai_enabled)}
                    style={{ cursor: (loading.fetchingPageInfo || loading.submitting) ? 'not-allowed' : 'pointer' }}
                  >
                    <div className="modern-switch-thumb"></div>
                  </div>
                </div>
              </div>

              {/* Status Field */}
              <div className="modern-form-group mb-0">
                <label className="modern-form-label">{t('LABEL_STATUS')}</label>
                <select
                  name="status"
                  className={`modern-form-control modern-select ${touched.status && errors.status ? 'input-error' : ''}`}
                  value={values.status || STATUS_CLIENT_WEBSITES_ACTIVE}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  disabled={loading.fetchingPageInfo || loading.submitting}
                >
                  {[STATUS_CLIENT_WEBSITES_ACTIVE, STATUS_CLIENT_WEBSITES_DISABLED].map(status => (
                    <option key={status} value={status}>
                      {t(`STATUS_${status.toUpperCase()}`)}
                    </option>
                  ))}
                </select>
                {touched.status && errors.status && (
                  <div className="error-message">
                    <i className="mdi mdi-alert-circle-outline"></i>
                    {errors.status}
                  </div>
                )}
              </div>
            </div>


            {/* Action Buttons */}
            <div className="form-actions">
              <button
                type="button"
                className="modern-btn st-btn-material-outline"
                disabled={loading.submitting || loading.fetchingPageInfo}
                onClick={() => onCancel && onCancel()}
              >
                <i className="mdi mdi-close"></i>
                {t('BTN_CANCEL')}
              </button>
              <button
                type="submit"
                className="modern-btn st-btn-material"
                disabled={loading.fetchingPageInfo || loading.submitting}
              >
                {loading.fetchingPageInfo ? (
                  <>
                    <div className="loading-spinner"></div>
                    {t('TXT_FETCHING_PAGE_INFO')}
                  </>
                ) : loading.submitting ? (
                  <>
                    <div className="loading-spinner"></div>
                    {t('TXT_LOADING')}
                  </>
                ) : (
                  <>
                    <i className={`mdi ${isEdit ? 'mdi-pencil' : 'mdi-plus'}`}></i>
                    {isEdit ? t('BTN_UPDATE') : t('BTN_CREATE')}
                  </>
                )}
              </button>
            </div>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default ClientWebsitesForm;