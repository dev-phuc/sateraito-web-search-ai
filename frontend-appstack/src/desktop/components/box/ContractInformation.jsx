import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';
import moment from 'moment';

// Library UI imports
import { Dropdown, Modal } from 'react-bootstrap';

// Hook components
import useTheme from '@/hooks/useTheme';

// Zustand
import useTenantConfigStore from '@/store/tenant_config';

// Constants

// Component
import MakerLoading from '@/desktop/components/MakerLoading';
import ContractInformationForm from '../form/ContractInformation';

const ContractInformationBox = ({ }) => {
  // Default hooks
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { tenant, app_id } = useParams();
  const { showNotice } = useTheme();

  // Zustand stores
  const { loading, contractInformation, fetchTenantConfig } = useTenantConfigStore();

  // Use state
  const [showEditModal, setShowEditModal] = useState(false);

  // Handler
  const isDuringTheContractPeriod = (startDate, endDate) => {
    const now = moment();
    const start = moment(startDate);
    const end = moment(endDate);
    return now.isBetween(start, end, null, '[]'); // Inclusive of start and end dates
  };

  const handlerLoadData = async () => {
    const { success, message } = await fetchTenantConfig(tenant, app_id);
    if (!success) {
      showNotice('error', message);
    }
  }

  const handlerToggleEditModal = () => {
    setShowEditModal(!showEditModal);
  };

  const handlerAfterSubmit = async () => {
    handlerLoadData();
    handlerToggleEditModal();
  };

  // Return the component
  return (
    <>
      <div className="bg-light pb-1">
        <div className="wrap-box">

          <div className="box-header d-flex align-items-center px-2 justify-content-between">
            <div className="box-header-left d-flex align-items-center justify-content-start">
              <span className="mdi mdi-license me-2"></span>
              <h5 className="mb-0">{t("CONTRACT_INFORMATION")}</h5>
            </div>
            {/* Menu */}
            <div>
              <Dropdown>
                <Dropdown.Toggle className="btn btn-sm btn-light rounded-circle">
                  <span className="mdi mdi-dots-vertical"></span>
                </Dropdown.Toggle>
                <Dropdown.Menu align="end">
                  <Dropdown.Item onClick={handlerToggleEditModal}>
                    <span className="mdi mdi-pencil-outline me-2"></span>
                    {t("BTN_EDIT")}
                  </Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
            </div>
          </div>

          <div className="box-content box-content">
            {contractInformation && (
              <>
                <div className="px-4 mb-3">
                  <p className='mb-2'>
                    <strong>{t("MAIL_ADDRESS")}:</strong> {contractInformation.mail_address || t("TXT_NOT_SET")}
                  </p>
                  <p className='mb-2'>
                    <strong>{t("TEL_NO")}:</strong> {contractInformation.tel_no || t("TXT_NOT_SET")}
                  </p>
                  <p className='mb-2'>
                    <strong>{t("CONTRACT_STATUS")}:</strong>
                    {isDuringTheContractPeriod(contractInformation.contract_start_date, contractInformation.cancel_date) ? (
                      <span className="text-success ms-2">
                        {t('MSG_ACTIVE_UNTIL')}
                      </span>
                    ) : (
                      <span className="text-secondary ms-2">
                        {t('MSG_INACTIVE_SINCE')}
                      </span>
                    )}
                  </p>
                  <p className='mb-2'>
                    <strong>{t("PERIOD_OF_CONTRACT")}:</strong> {contractInformation.charge_start_date} ～ {contractInformation.cancel_date}
                  </p>
                </div>

                {/* Warning message */}
                <div className="box-warning px-4">
                  <div className="alert mb-0">
                    <span className="mb-0 text-warning">
                      {t("PLEASE_CONTACT_SATERAITO_TO_CONTINUE_AFTER_TRIAL")}
                    </span>
                  </div>
                </div>
              </>
            )}

            {loading && <MakerLoading opacity="10" />}
          </div>
        </div>
      </div>

      {/* Edit Modal */}
      <Modal show={showEditModal} onHide={handlerToggleEditModal} centered>
        <Modal.Header closeButton>
          <Modal.Title>{t("EDIT_CONTRACT_INFORMATION")}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <ContractInformationForm
            tenant={tenant}
            app_id={app_id}
            onCancel={handlerToggleEditModal}
            afterSubmit={handlerAfterSubmit}
          />
        </Modal.Body>
      </Modal>
    </>
  );
};

export default ContractInformationBox;