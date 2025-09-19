import { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

// Library UI imports
import { Dropdown } from 'react-bootstrap';

// Hook components

// Zustand

// Constants

// Components
import OperationLogsMiniTable from '@/desktop/components/table/OperationLogMini';

const OperationLogBox = ({ }) => {
  // Default hooks
  const navigate = useNavigate();
  const { tenant, app_id } = useParams();
  const { t } = useTranslation();

  // Zustand stores

  // Use state

  // Handler
  const handlerOnClickDetail = () => {
    navigate(`/${tenant}/${app_id}/admin_console/logs`);
  }

  // Return the component
  return (
    <>
      <div className="bg-light pb-1">
        <div className="wrap-box">
          <div className="box-header d-flex align-items-center px-2 justify-content-between">
            <div className="box-header-left d-flex align-items-center justify-content-start">
              <span className="mdi mdi-file-document-outline me-2"></span>
              <h5 className="mb-0">{t("TXT_OPERATIONS_LOGS")}</h5>
            </div>
            {/* Menu */}
            <div>
              <Dropdown>
                <Dropdown.Toggle className="btn btn-sm btn-light rounded-circle">
                  <span className="mdi mdi-dots-vertical"></span>
                </Dropdown.Toggle>
                <Dropdown.Menu align="end">
                  <Dropdown.Item onClick={handlerOnClickDetail}>
                    <span className="mdi mdi-information-outline me-2"></span>
                    {t("BTN_MORE_DETAIL_OPERATION_LOGS")}
                  </Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
            </div>
          </div>

          <div className="box-content px-4">
            <OperationLogsMiniTable />
          </div>
        </div>
      </div>
    </>
  );
};

export default OperationLogBox;