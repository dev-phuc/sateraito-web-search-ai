import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import moment from 'moment';

// Library UI imports
import { Dropdown } from 'react-bootstrap';

// Hook components

// Zustand
import useTenantConfigStore from '@/store/tenant_config';

// Constants

const ContractInformationBox = ({ }) => {
  // Default hooks
  const { t } = useTranslation();

  // Zustand stores
  const { contractInformation } = useTenantConfigStore();

  // Use state

  // Handler
  const isDuringTheContractPeriod = (startDate, endDate) => {
    const now = moment();
    const start = moment(startDate);
    const end = moment(endDate);
    return now.isBetween(start, end, null, '[]'); // Inclusive of start and end dates
  };

  if (!contractInformation) {
    return <>
    </>
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
                  <Dropdown.Item href="#/action-1">
                    <span className="mdi mdi-pencil-outline me-2"></span>
                    {t("BTN_EDIT")}
                  </Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
            </div>
          </div>

          <div className="box-content box-content px-4">
            <div>
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
          </div>

          {/* Warning message */}
          <div className="box-warning px-4">
            <div className="alert mb-0">
              <span className="mb-0 text-warning">
                {t("PLEASE_CONTACT_SATERAITO_TO_CONTINUE_AFTER_TRIAL")}
              </span>
            </div>
          </div>

        </div>
      </div>
    </>
  );
};

export default ContractInformationBox;