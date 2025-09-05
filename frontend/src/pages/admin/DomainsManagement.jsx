import { useRef, useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router';

// Ant Design components
import { Button, Modal } from 'antd';
import { GlobalOutlined, PlusOutlined } from '@ant-design/icons';

// Custom components
import ClientWebsitesForm from '@/components/form/ClientWebsites';
import ClientWebsitesTable from '@/components/table/ClientWebsites';

// Zustand
import useStoreClientWebsites from '@/store/client_websites';

const DomainsManagement = () => {
  // Default hooks
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { tenant, app_id } = useParams();

  // Zustand stores
  const { isLoading, fetchClientWebsites, deleteClientWebsites } = useStoreClientWebsites();

  // States
  const [isModalFormVisible, setIsModalFormVisible] = useState(false);
  const [selectedEditData, setSelectedEditData] = useState(null);

  // Handlers
  const handleSelectEdit = (data) => {
    setSelectedEditData(data);
    setIsModalFormVisible(true);
  };

  const handleSubmitDelete = (data) => {
    deleteClientWebsites(tenant, app_id, data.id)
  };

  const handleAfterSubmit = (success) => {
    setIsModalFormVisible(false);
    setSelectedEditData(null);
    
    if (success) {
      fetchClientWebsites(tenant, app_id);
    }
  };

  const handleCloseModal = () => {
    setIsModalFormVisible(false);
    setSelectedEditData(null);
  };

  // Effects
  useEffect(() => {
    if (!isLoading) {
      fetchClientWebsites(tenant, app_id);
    }
  }, []);

  // Return the component
  return (
    <div className="h-full">
      <div className="flex flex-col h-full">

        {/* Toolbar */}
        <div className="mx-2 my-3 flex justify-between items-center">
          {/* Toolbar left */}
          <div>
            <h1 className="text-xl font-bold">
              <GlobalOutlined />&nbsp;{t('TITLE_CLIENT_WEBSITES_MANAGEMENT')}
            </h1>
          </div>

          {/* Toolbar right */}
          <div>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setIsModalFormVisible(true)}
            >
              {t('BTN_ADD_DOMAIN')}
            </Button>
          </div>
        </div>

        {/* Table */}
        <ClientWebsitesTable
          tenant={tenant} app_id={app_id}
          onSelectEdit={handleSelectEdit}
          onSubmitDelete={handleSubmitDelete}
        />

        {/* Modal Form */}
        <Modal
          title={t('TITLE_ADD_DOMAIN')}
          open={isModalFormVisible}
          onCancel={handleCloseModal}
          footer={null}
          destroyOnHidden
        >
          <ClientWebsitesForm
            tenant={tenant}
            app_id={app_id}
            data={selectedEditData}
            afterSubmit={handleAfterSubmit}
          />
        </Modal>
      </div>
    </div>
  );
};

export default DomainsManagement;
