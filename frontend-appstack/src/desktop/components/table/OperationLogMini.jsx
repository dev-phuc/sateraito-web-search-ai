import { useRef, useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';

// Library UI imports
import { Card, Table, Spinner, Modal } from "react-bootstrap";

// Utils

// Constants

// Components
import SearchOperationLogForm from '@/desktop/components/form/SearchOperationLog';
import DetailOperationLogPanel from "@/desktop/components/panel/DetailOperationLog";

// Zustand
import useStoreOperationLogs from '@/store/operation_log';

const OperationLogsMiniTable = ({ }) => {
  // Default hooks
  const { tenant, app_id } = useParams();
  const navigate = useNavigate();
  const { t } = useTranslation();

  // Zustand stores
  const { fetchOperationLogs, isLoading, total, isHaveMore, operationLogs } = useStoreOperationLogs();

  const optionsLimit = [5, 10, 20, 50, 100];
  const columnsTable = [
    // { key: 'tenant', width: '150px', label: t('NAME_COL_TENANT') },
    // { key: 'app_id', width: '100px', label: t('NAME_COL_APP_ID') },
    {
      key: 'client_domain', width: '170px', label: t('NAME_COL_CLIENT_DOMAIN'),
      render: (value) => (<div style={{
        display: '-webkit-box',
        WebkitLineClamp: 1,
        WebkitBoxOrient: 'vertical',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'normal',
      }}>{value || '-'}</div>)
    },
    {
      key: 'model_name', width: '120px', label: t('NAME_COL_MODEL_NAME'),
      render: (value) => {
        let displayValue = value || '-';
        if (value && value.length > 15) {
          displayValue = value.substring(0, 15) + '...';
        }

        return <div style={{
          display: '-webkit-box',
          WebkitLineClamp: 1,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'normal',
          textAlign: 'center'
        }}>
          <span className='badge bg-info'>{displayValue}</span>
        </div>;
      }
    },
    {
      key: 'status', width: '120px', label: t('NAME_COL_STATUS'),
      render: (value) => {
        let className = 'bg-secondary';
        let text = value || '-';

        if (value === 'completed') { className = 'bg-success'; text = t('STATUS_COMPLETED'); }
        else if (value === 'failed') { className = 'bg-danger'; text = t('STATUS_FAILED'); }
        else if (value === 'pending') { className = 'bg-warning text-dark'; text = t('STATUS_PENDING'); }
        else if (value === 'processing') { className = 'bg-info text-dark'; text = t('STATUS_PROCESSING'); }

        return <div className='text-center'>
          <span className={`badge ${className}`}>{text}</span>
        </div>;
      }
    },
    { key: 'created_date', label: t('NAME_COL_CREATED_AT'), width: '140px' },
  ];

  // States
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(optionsLimit[1]); // Default 10
  const [listPages, setListPages] = useState([]);
  const [paramsSearch, setParamsSearch] = useState({
    client_domain: '',
    from_date: '',
    to_date: '',
  });
  const [showDetailLog, setShowDetailLog] = useState(false);
  const [detailLogData, setDetailLogData] = useState(null);

  // Effects
  useEffect(() => {
    if (tenant && app_id) {
      fetchOperationLogs(tenant, app_id, page, limit, paramsSearch);
    }
  }, [tenant, app_id, page, limit, paramsSearch]);

  useEffect(() => {
    // Generate list pages
    // Show max 10 pages, with "..." if more than 10 pages
    const totalPages = Math.ceil(total / limit);
    let pages = [];
    if (totalPages <= 10) {
      pages = Array.from({ length: totalPages }, (_, i) => i + 1);
    }
    else {
      if (page <= 6) {
        pages = [...Array(8).keys()].map(i => i + 1);
        pages.push('...');
        pages.push(totalPages);
      }
      else if (page >= totalPages - 5) {
        pages = [1, '...'];
        pages = pages.concat([...Array(8).keys()].map(i => totalPages - 8 + i + 1));
      }
      else {
        pages = [1, '...'];
        pages = pages.concat([...Array(5).keys()].map(i => page - 2 + i + 1));
        pages.push('...');
        pages.push(totalPages);
      }
    }

    setListPages(pages);

  }, [operationLogs, total, limit]);

  // Handler
  const handlerClickRow = (item) => {
    setDetailLogData(item);
    setShowDetailLog(true);
  }

  // Render only tenant, app_id, client_domain
  const renderWebsiteItem = (item, index) => (
    <tr key={item.id || index} className="align-middle" onClick={() => handlerClickRow(item)} style={{ cursor: 'pointer' }}>
      {columnsTable.map((col) => {

        let style = {};
        if (col.width) {
          style.width = col.width;
          style.maxWidth = col.width;
          style.overflow = 'hidden';
          style.textOverflow = 'ellipsis';
          style.whiteSpace = 'nowrap';
        }

        if (col.render) {
          return (<td key={col.key} style={style}>{col.render(item[col.key])}</td>)
        }

        return (<td key={col.key} style={style}>{item[col.key] || '-'}</td>)
      })}
    </tr>
  );

  const handlerSubmitSearch = (values) => {
    setParamsSearch(values);
    setPage(1);
  };

  // Return the component
  return (
    <div className="operation-logs-table">
      <Card className="shadow-none border-0">
        {/* Table Body */}
        <Card.Body className="p-0" >
          <div className="table-responsive">
            <Table className="mb-0" hover>
              <thead className="table-light">
                <tr>
                  {columnsTable.map((col) => (
                    <th key={col.key}>{col.label}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {operationLogs.map((item, index) => renderWebsiteItem(item, index))}
                {operationLogs.length === 0 && !isLoading && (
                  <tr>
                    <td colSpan={columnsTable.length} className="text-center py-5">
                      <div className="text-muted">
                        <i className="mdi mdi-web-off mdi-48px d-block mb-3 opacity-50"></i>
                        <h6 className="fw-normal">{t('NO_OPERATION_LOGS_AVAILABLE')}</h6>
                        <p className="small mb-0">{t('TXT_NO_OPERATION_LOGS_AVAILABLE_DESC')}</p>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </Table>
          </div>

          {/* Loading Indicator */}
          {isLoading && (
            <div className="position-absolute top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center bg-white bg-opacity-75">
              <div className="text-center">
                <Spinner animation="border" variant="primary" />
                <div className="mt-2 text-muted small">{t('MSG_DATA_OPERATION_LOGS_LOADING')}</div>
              </div>
            </div>
          )}
        </Card.Body>
      </Card >

      {/* Modal Detail Log */}
      <Modal
        show={showDetailLog}
        onHide={() => setShowDetailLog(false)}
        size="lg"
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>{t('TITLE_DETAIL_OPERATION_LOG')}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <DetailOperationLogPanel data={detailLogData} />
        </Modal.Body>
      </Modal>
    </div >
  );
};

export default OperationLogsMiniTable;
