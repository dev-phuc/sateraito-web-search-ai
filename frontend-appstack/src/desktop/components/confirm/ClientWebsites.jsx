import { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';

// Library UI imports
import { Button } from "react-bootstrap";

// Hook components
import useTheme from '@/hooks/useTheme'

// Zustand
import useStoreClientWebsites from '@/store/client_websites';

const ClientWebsitesConfirmDelete = ({ tenant, app_id, data, onCancel, afterSubmit }) => {
  // Default hooks
  const { t } = useTranslation();
  const { showNotice } = useTheme();

  // Zustand stores
  const { deleteClientWebsites } = useStoreClientWebsites();

  const [loading, setLoading] = useState(false);

  const processDeleteSingle = async () => {
    const result = await deleteClientWebsites(tenant, app_id, data.id);
    return result;
  };
  const processDeleteMultiple = async () => {
    const results = await Promise.all(
      data.id.map(id => deleteClientWebsites(tenant, app_id, id))
    );
    const failed = results.filter(r => !r.success);
    const isSuccess = failed.length === 0;
    let message = '';
    if (!isSuccess) {
      message = failed.map(r => t(r.error) || t('TXT_ERROR_DELETE_CLIENT_WEBSITES')).join('\n');
    }
    return { success: isSuccess, message };
  }

  const handleDelete = useCallback(async () => {
    if (loading) return;
    setLoading(true);

    let result;
    if (Array.isArray(data?.id)) {
      result = await processDeleteMultiple();
    }
    else {
      result = await processDeleteSingle();
    }

    let { success, error, message } = result;
    if (success) {
      message = t('TXT_DELETE_CLIENT_WEBSITES_SUCCESS');
      showNotice('success', message);

      if (afterSubmit) {
        afterSubmit(success);
      }
    } else {
      if (!message) {
        message = t(error) || t('TXT_ERROR_DELETE_CLIENT_WEBSITES');
      }
      showNotice('error', message);
    }

    setLoading(false);
  }, [loading, deleteClientWebsites, tenant, app_id, data?.id, t, afterSubmit]);

  // Return the component
  return (
    <div className="text-center">
      <p>{t('CONFIRM_DELETE_CLIENT_WEBSITE')}</p>
      <div className="d-flex justify-content-center gap-2 mt-3 pb-4">
        <Button
          variant="outline-secondary"
          disabled={loading}
          onClick={() => onCancel && onCancel()}
        >
          <i className="mdi mdi-close me-1"></i>
          {t('BTN_CANCEL')}
        </Button>
        <Button
          variant="danger"
          disabled={loading}
          onClick={handleDelete}
        >
          <i className="mdi mdi-delete me-1"></i>
          {loading ? t('TXT_LOADING') + '...' : t('BTN_DELETE')}
        </Button>
      </div>
    </div>
  );
};

export default ClientWebsitesConfirmDelete;