import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

// Library UI imports

// Hook components

// Zustand
import useTenantConfigStore from '@/store/tenant_config';

// Constants

const TenantInformationBox = ({ }) => {
  // Default hooks
  const { t } = useTranslation();

  // Zustand stores
  const { contractInformation } = useTenantConfigStore();

  // Use state

  // Handler

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
              <span className="mdi mdi-hexagon-multiple me-2"></span>
              <h5 className="mb-0">{t("TENANT_INFORMATION")}</h5>
            </div>
            {/* Menu */}
            <div>
              {/* <button className="btn btn-sm btn-light rounded-circle" type="button">
                <span className="mdi mdi-dots-vertical mdi-24px"></span>
              </button> */}
            </div>
          </div>

          <div className="box-content px-4">
            <div>
              <p className='mb-2'>
                <strong>{t("TENANT")}:</strong> {contractInformation.tenant}
              </p>
              <p className='mb-2'>
                <strong>{t("APP_ID")}:</strong> {contractInformation.app_id}
              </p>
              <p className='mb-2'>
                <strong>{t("TARGET_LINK_DOMAINS")}:</strong> {contractInformation.target_link_domains || t("TXT_NOT_SET")}
              </p>
            </div>
          </div>

          {/* Warning message */}
          <div className="box-warning px-4">
            <div className="alert mb-0">
              <span className="mb-0 text-warning">
                {t("PLEASE_CONTACT_SATERAITO_IF_YOU_WANT_TO_USE_SUBDOMAIN_AS_WELL")}
              </span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default TenantInformationBox;