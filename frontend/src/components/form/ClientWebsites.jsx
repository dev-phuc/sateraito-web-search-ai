import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';
import { Form, Input, Switch, Select, Button, Avatar } from 'antd';
import { GlobalOutlined, PlusOutlined, EditOutlined, CloseOutlined } from '@ant-design/icons';

// Requests API
import { getPageInfoByUrl } from '@/request/sateraitoUtils';

// Zustand
import useStoreApp from '@/store/app';
import useStoreClientWebsites from '@/store/client_websites';

// Constants
import { STATUS_CLIENT_WEBSITES_ACTIVE, STATUS_CLIENT_WEBSITES_DISABLED } from '@/constant';

const { TextArea } = Input;

const ClientWebsitesForm = ({ tenant, app_id, data, afterSubmit }) => {
  // Default hooks
  const navigate = useNavigate();
  const { t } = useTranslation();

  // Zustand stores
  const { setMessageNotify } = useStoreApp();
  const { createClientWebsites, editClientWebsites } = useStoreClientWebsites();

  const [form] = Form.useForm();
  const [isEdit] = useState(!!data);
  const [loading, setLoading] = useState({
    submitting: false,
    fetchingPageInfo: false,
  });
  const [faviconUrl, setFaviconUrl] = useState(data?.favicon_url || null);
  const [pageInfoCache, setPageInfoCache] = useState({});

  useEffect(() => {
    if (data) {
      form.setFieldsValue({
        domain: data.domain,
        favicon_url: data.favicon_url,
        site_name: data.site_name,
        description: data.description,
        ai_enabled: data.ai_enabled,
        status: data.status,
      });
    }
  }, [data, form]);

  const handleDomainBlur = useCallback(async (e) => {
    const url = e.target.value;
    if (!url) return;

    if (pageInfoCache[url]) {
      const pageInfo = pageInfoCache[url];
      form.setFieldsValue({
        favicon_url: pageInfo.favicon_url || '',
        site_name: pageInfo.site_name || '',
        description: pageInfo.description || '',
      });
      setFaviconUrl(pageInfo.favicon_url);
      return;
    }

    setLoading(l => ({ ...l, fetchingPageInfo: true }));
    try {
      const pageInfo = await getPageInfoByUrl(url);
      if (pageInfo) {
        form.setFieldsValue({
          favicon_url: pageInfo.favicon_url,
          site_name: pageInfo.site_name,
          description: pageInfo.description,
        });
        setFaviconUrl(pageInfo.favicon_url);
        setPageInfoCache(prev => ({ ...prev, [url]: pageInfo }));
      }
    } catch (error) {
      let message = error?.response?.data?.message;
      if (message === 'failed_to_fetch_page') {
        message = 'MSG_WARNING_FETCH_PAGE_INFO';
      }
      setMessageNotify({ type: 'warning', text: message });
    } finally {
      setLoading(l => ({ ...l, fetchingPageInfo: false }));
    }
  }, [tenant, app_id, form, pageInfoCache, setMessageNotify]);

  const handleSubmit = useCallback(async (values) => {
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
      setMessageNotify({ type: 'success', text: message });
    } else {
      message = t(error);
      if (message === error) {
        message = isEdit ? t('TXT_ERROR_UPDATE_CLIENT_WEBSITES') : t('TXT_ERROR_CREATE_CLIENT_WEBSITES');
      }
      setMessageNotify({ type: 'error', text: message });
    }
    setLoading(l => ({ ...l, submitting: false }));

    if (afterSubmit) {
      afterSubmit(success);
    }

  }, [loading.submitting, createClientWebsites, tenant, app_id, isEdit, setMessageNotify, t]);

  // Return the component
  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleSubmit}
      initialValues={{
        ai_enabled: true,
        status: STATUS_CLIENT_WEBSITES_ACTIVE,
      }}
    >
      {/* Avatar center form */}
      <Avatar size={64} src={faviconUrl} style={{ display: 'block', margin: '0 auto 20px' }} icon={<GlobalOutlined />} />

      {/* Form items */}
      <Form.Item
        label={t('LABEL_DOMAIN')}
        name="domain"
        rules={[
          { required: true, message: t('MSG_ERROR_DOMAIN_REQUIRED') },
          { pattern: /^(https?:\/\/)?([\w-]+(\.[\w-]+)+)(\/[\w-./?%&=]*)?$/, message: t('MSG_ERROR_DOMAIN_INVALID') },
        ]}
      >
        <Input
          disabled={isEdit || loading.fetchingPageInfo || loading.submitting}
          suffix={loading.fetchingPageInfo ? t('TXT_LOADING') + '...' : null}
          onBlur={handleDomainBlur}
          placeholder={t('PLACEHOLDER_CLIENT_WEBSITES_DOMAIN')}
        />
      </Form.Item>
      <Form.Item
        label={t('LABEL_FAVICON_URL')}
        name="favicon_url"
      >
        <Input
          disabled={loading.fetchingPageInfo || loading.submitting}
          onChange={e => setFaviconUrl(e.target.value)}
          placeholder={t('PLACEHOLDER_CLIENT_WEBSITES_FAVICON_URL')}
        />
      </Form.Item>
      <Form.Item
        label={t('LABEL_SITE_NAME')}
        name="site_name"
      >
        <Input
          disabled={loading.fetchingPageInfo || loading.submitting}
          placeholder={t('PLACEHOLDER_CLIENT_WEBSITES_SITE_NAME')}
        />
      </Form.Item>
      <Form.Item
        label={t('LABEL_DESCRIPTION')}
        name="description"
      >
        <TextArea
          disabled={loading.fetchingPageInfo || loading.submitting}
          rows={3}
          placeholder={t('PLACEHOLDER_CLIENT_WEBSITES_DESCRIPTION')}
        />
      </Form.Item>
      <Form.Item
        label={t('LABEL_AI_ENABLED')}
        name="ai_enabled"
        valuePropName="checked"
      >
        <Switch
          disabled={loading.fetchingPageInfo || loading.submitting}
        />
      </Form.Item>
      <Form.Item
        label={t('LABEL_STATUS')}
        name="status"
        rules={[{ required: true, message: t('MSG_ERROR_STATUS_REQUIRED') }]}
      >
        <Select
          disabled={loading.fetchingPageInfo || loading.submitting}
        >
          {[STATUS_CLIENT_WEBSITES_ACTIVE, STATUS_CLIENT_WEBSITES_DISABLED].map(status => (
            <Select.Option key={status} value={status}>
              {t(`STATUS_${status.toUpperCase()}`)}
            </Select.Option>
          ))}
        </Select>
      </Form.Item>
      <Form.Item className='wrap-form-submit-button'>
        <div className="flex justify-end">
          <Button
            type='default'
            className='mr-2'
            danger
            disabled={loading.submitting || loading.fetchingPageInfo}
            icon={<CloseOutlined />}
            onClick={() => afterSubmit(false)}
          >
            {t('BTN_CANCEL')}
          </Button>
          <Button
            type="primary"
            htmlType="submit"
            loading={loading.submitting}
            disabled={loading.fetchingPageInfo || loading.submitting}
            icon={isEdit ? <EditOutlined /> : <PlusOutlined />}
          >
            {isEdit ? t('BTN_UPDATE') : t('BTN_CREATE')}
          </Button>
        </div>
      </Form.Item>
    </Form>
  );
};

export default ClientWebsitesForm;