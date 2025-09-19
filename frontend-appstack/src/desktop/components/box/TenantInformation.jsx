import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

// Library UI imports

// Hook components

// Zustand
import useTenantConfigStore from '@/store/tenant_config';

// Constants

// Component
import MakerLoading from '@/desktop/components/MakerLoading';

const TenantInformationBox = ({ }) => {
  // Default hooks
  const { t } = useTranslation();

  // Zustand stores
  const { loading, contractInformation } = useTenantConfigStore();

  // Use state

  // Handler

  // Return the component
  return (
    <>
      <div className="bg-light">
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

          <div className="box-content position-relative pb-2">
            {contractInformation && (
              <>
                <div className="px-4">
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
                <div className="box-warning px-4">
                  <div className="alert mb-0">
                    <span className="mb-0 text-warning">
                      {t("PLEASE_CONTACT_SATERAITO_IF_YOU_WANT_TO_USE_SUBDOMAIN_AS_WELL")}
                    </span>
                  </div>
                </div>
              </>
            )}

            {loading && <MakerLoading opacity="10"/>}
          </div>
        </div>
      </div>
    </>
  );
};

export default TenantInformationBox;