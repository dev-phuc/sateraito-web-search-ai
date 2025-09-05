// Framework import
import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Helmet } from "react-helmet-async";
import { useNavigate, useParams } from 'react-router-dom';

// Components 
import { Modal } from "react-bootstrap";

// Zustand
import useStoreClientWebsites from '@/store/client_websites';

// Hook components
import useTheme from "@/hooks/useTheme";

// Context components

// Library imports
// Library IU imports
import { Container } from "react-bootstrap";

// Constant value

// Components
import ClientWebsitesTable from "@/desktop/components/table/ClientWebsites";
import ClientWebsitesForm from "@/desktop/components/form/ClientWebsites";
import ClientWebsitesConfirmDelete from "@/desktop/components/confirm/ClientWebsites";

// Define the component
const DashboardAdminConsolePage = () => {
  // Default hooks
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { tenant, app_id } = useParams();

  // Zustand stores
  const { isLoading, clientWebsites, fetchClientWebsites, deleteClientWebsites } = useStoreClientWebsites();

  // Use hooks state
  const { showNotice } = useTheme();

  // state
  const [itemSelected, setItemSelected] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [dataEdit, setDataEdit] = useState(null);
  const [showConfirmDelete, setShowConfirmDelete] = useState(false);
  const [dataDelete, setDataDelete] = useState(null);

  // Handler method
  const onChangeSelectAllChecked = (checked) => {
    if (checked) {
      const allIds = clientWebsites.map(item => item.id);
      setItemSelected(allIds);
    }
    else {
      setItemSelected([]);
    }
  };
  const onChangeSelectOneChecked = (id, checked) => {
    if (checked) {
      setItemSelected(prev => [...prev, id]);
    }
    else {
      setItemSelected(prev => prev.filter(itemId => itemId !== id));
    }
  };

  const onCreateClientWebsite = () => {
    setShowForm(true);
  };

  const onCloseForm = () => {
    setShowForm(false);
    setDataEdit(null);
  };

  const onEditClientWebsite = (item) => {
    setShowForm(true);
    setDataEdit(item);
  };

  const onDeleteClientWebsite = (item) => {
    setShowConfirmDelete(true);
    setDataDelete(item);
  };
  const onDeleteSelectedWebsites = () => {
    if (itemSelected.length === 0) {
      showNotice('warning', t('TXT_SELECT_AT_LEAST_ONE_ITEM'));
      return;
    }
    setShowConfirmDelete(true);
    setDataDelete({ id: itemSelected }); // Pass array of IDs
  };
  const onCloseConfirmDelete = () => {
    setShowConfirmDelete(false);
    setDataDelete(null);
  };
  const afterDeleteClientWebsite = (success) => {
    if (success) {
      fetchClientWebsites(tenant, app_id);
    }
    setItemSelected([]);
    onCloseConfirmDelete();
  };

  // Effects
  useEffect(() => {
    if (!isLoading) {
      fetchClientWebsites(tenant, app_id);
    }
  }, []);

  // Return component
  return (
    <>
      <Helmet>
        <title>{t("PAGE_TITLE_CLIENT_WEBSITES")}</title>
      </Helmet>

      <Container fluid className="p-0">
        <ClientWebsitesTable
          tenant={tenant}
          app_id={app_id}
          isLoading={isLoading}
          checkedList={itemSelected}
          onChangeSelectAllChecked={onChangeSelectAllChecked}
          onChangeSelectChecked={onChangeSelectOneChecked}
          onCreateClientWebsite={onCreateClientWebsite}
          onEditClientWebsite={onEditClientWebsite}
          onReload={() => fetchClientWebsites(tenant, app_id)}
          onDeleteClientWebsite={onDeleteClientWebsite}
          onDeleteSelectedWebsites={onDeleteSelectedWebsites}
        />
      </Container>


      {/* Modal Form */}
      <Modal
        show={showForm}
        onHide={onCloseForm}
        size="lg"
        centered
        backdrop="static"
        scrollable
        animation={false}
      >
        <Modal.Header closeButton>
          <Modal.Title>{t("PAGE_TITLE_CLIENT_WEBSITES")}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <ClientWebsitesForm
            tenant={tenant}
            app_id={app_id}
            data={dataEdit}
            onCancel={onCloseForm}
            afterSubmit={() => {
              fetchClientWebsites(tenant, app_id);
              onCloseForm();
            }}
          />
        </Modal.Body>
      </Modal>

      {/* Modal Confirm Delete */}
      <Modal
        show={showConfirmDelete}
        onHide={onCloseConfirmDelete}
        size="md"
        centered
        backdrop="static"
        scrollable
        animation={false}
      >
        <Modal.Header closeButton>
          <Modal.Title>{t("TITLE_CONFIRM_DELETE_CLIENT_WEBSITE")}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <ClientWebsitesConfirmDelete
            tenant={tenant}
            app_id={app_id}
            data={dataDelete}
            onCancel={onCloseConfirmDelete}
            afterSubmit={afterDeleteClientWebsite}
          />
        </Modal.Body>
      </Modal>
    </>
  );
};

export default DashboardAdminConsolePage;
