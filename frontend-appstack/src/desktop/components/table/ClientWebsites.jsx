import { useRef, useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';

// Library UI imports
import {
  Card,
  Form,
  Button,
  Table,
  Spinner,
  Badge,
  OverlayTrigger,
  Tooltip
} from "react-bootstrap";

// Utils
import { formatDate, truncateText } from '@/utils';

// Constants
import { STATUS_CLIENT_WEBSITES_ACTIVE, STATUS_CLIENT_WEBSITES_DISABLED, STATUS_CLIENT_WEBSITES_OVER_QUOTA } from '@/constants';

// Zustand
import useStoreClientWebsites from '@/store/client_websites';

// Components
import SearchClientWebsitesForm from "@/desktop/components/form/SearchClientWebsites";

const ClientWebsitesTable = ({
  tenant,
  app_id,
  checkedList = [],
  onChangeSelectAllChecked,
  onChangeSelectChecked,
  onCreateClientWebsite,
  onEditClientWebsite,
  onDeleteClientWebsite,
  onDeleteSelectedWebsites,
  onReload
}) => {
  // Default hooks
  const navigate = useNavigate();
  const { t } = useTranslation();

  // Zustand stores
  const { isLoading, clientWebsites, setClientWebsites, fetchClientWebsites } = useStoreClientWebsites();

  // States

  // Helper function to get status badge
  const getStatusBadge = (status) => {
    let statusConfig = {};
    statusConfig[STATUS_CLIENT_WEBSITES_ACTIVE] = { bg: 'success', text: t('STATUS_ACTIVE') };
    statusConfig[STATUS_CLIENT_WEBSITES_DISABLED] = { bg: 'danger', text: t('STATUS_DISABLED') };
    statusConfig[STATUS_CLIENT_WEBSITES_OVER_QUOTA] = { bg: 'warning', text: t('STATUS_OVER_QUOTA') };

    const config = statusConfig[status?.toLowerCase()] || { bg: 'secondary', text: status || 'Unknown' };
    return <Badge bg={config.bg} pill>{config.text}</Badge>;
  };

  const handlerOnSearch = (filters) => {
    const { domain, site_name, status } = filters;

    if (filters && (domain || site_name || status)) {
      // Filter client websites based clientWebsites in the store
      const filteredWebsites = clientWebsites.filter(website => {
        let matches = true;
        if (domain) {
          matches = matches && website.domain.toLowerCase().includes(domain.toLowerCase());
        }
        if (site_name) {
          matches = matches && website.site_name && website.site_name.toLowerCase().includes(site_name.toLowerCase());
        }
        if (status) {
          matches = matches && website.status && website.status.toLowerCase() === status.toLowerCase();
        }
        return matches;
      });
      // Update the clientWebsites in the store to the filtered list
      setClientWebsites(filteredWebsites);
    } else {
      fetchClientWebsites(tenant, app_id);
    }
  };

  // Render website item row
  const renderWebsiteItem = (item, index) => (
    <tr key={item.id} className="align-middle">
      <td className="text-center" style={{ width: '40px' }}>
        <input
          type="checkbox"
          className="form-check-input"
          checked={checkedList.includes(item.id)}
          onChange={(e) => onChangeSelectChecked && onChangeSelectChecked(item.id, e.target.checked)}
        />
      </td>

      <td className="text-center" style={{ width: '60px' }}>
        <div className="d-flex justify-content-center align-items-center">
          {item.favicon_url ? (
            <img
              src={item.favicon_url}
              alt={item.site_name || 'Website'}
              className="rounded"
              style={{
                width: '32px',
                height: '32px',
                objectFit: 'cover',
                border: '1px solid #e0e6ed'
              }}
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'flex';
              }}
            />
          ) : null}
          <div
            className="justify-content-center align-items-center bg-light rounded"
            style={{
              width: '32px',
              height: '32px',
              display: item.favicon_url ? 'none' : 'flex'
            }}
          >
            <i className="mdi mdi-web text-muted"></i>
          </div>
        </div>
      </td>

      <td>
        <div className="d-flex flex-column">
          <a
            href={item.domain}
            target="_blank"
            rel="noopener noreferrer"
            className="fw-semibold text-decoration-none mb-1"
            style={{ fontSize: '0.95rem' }}
          >
            {truncateText(item.domain, 35)}
          </a>
          {item.site_name && (
            <small className="text-muted">
              {truncateText(item.site_name, 30)}
            </small>
          )}
        </div>
      </td>

      <td>
        <OverlayTrigger
          placement="top"
          overlay={
            <Tooltip>
              {item.description || 'No description available'}
            </Tooltip>
          }
        >
          <span className="text-muted" style={{ cursor: 'help' }}>
            {truncateText(item.description, 40)}
          </span>
        </OverlayTrigger>
      </td>

      <td>
        {/* Switch for ai_enabled */}
        {item.ai_enabled ? (
          <Form.Check type="switch" id={`ai_enabled_${item.id}`} label="AI" checked disabled />
        ) : (
          <Form.Check type="switch" id={`ai_enabled_${item.id}`} label="AI" disabled />
        )}
      </td>

      <td>
        <div className="text-center">
          {getStatusBadge(item.status)}
        </div>
      </td>

      <td>
        <small className="text-muted">
          {formatDate(item.created_date)}
        </small>
      </td>

      <td>
        <small className="text-muted">
          {formatDate(item.updated_date)}
        </small>
      </td>

      <td>
        <div className="d-flex gap-1 justify-content-center">
          <OverlayTrigger
            placement="top"
            overlay={<Tooltip>{t('Edit Website')}</Tooltip>}
          >
            <Button
              variant="outline-primary"
              className="btn-icon"
              disabled={item.isEditing || item.isRemoving}
              onClick={() => onEditClientWebsite && onEditClientWebsite(item)}
            >
              {item.isEditing ? (
                <Spinner animation="border" />
              ) : (
                <i className="mdi mdi-pencil"></i>
              )}
            </Button>
          </OverlayTrigger>

          <OverlayTrigger
            placement="top"
            overlay={<Tooltip>{t('Delete Website')}</Tooltip>}
          >
            <Button
              variant="outline-danger"
              className="btn-icon"
              disabled={item.isUpdating || item.isRemoving}
              onClick={() => onDeleteClientWebsite && onDeleteClientWebsite(item)}
            >
              {item.isRemoving ? (
                <Spinner animation="border" />
              ) : (
                <i className="mdi mdi-delete"></i>
              )}
            </Button>
          </OverlayTrigger>
        </div>
      </td>
    </tr>
  );

  // Return the component
  return (
    <div className="client-websites-table">
      <Card className="shadow-none border-0">
        {/* Header Toolbar */}
        <Card.Header className="bg-white border-bottom">
          <div className="d-flex justify-content-between align-items-center">
            <div className="">
              {/* Search Form */}
              <SearchClientWebsitesForm
                tenant={tenant}
                app_id={app_id}
                isLoading={isLoading}
                onSearch={handlerOnSearch}
              />
            </div>

            <div className="text-muted small">
              <div className="d-flex gap-2">
                {checkedList.length > 0 && (
                  <Button
                    variant="outline-danger"
                    disabled={isLoading}
                    onClick={() => onDeleteSelectedWebsites && onDeleteSelectedWebsites()}
                  >
                    <i className="mdi mdi-delete"></i>
                    Delete ({checkedList.length})
                  </Button>
                )}
                <Button
                  variant="primary"
                  type="button"
                  disabled={isLoading}
                  onClick={() => onCreateClientWebsite && onCreateClientWebsite()}
                >
                  <i className="mdi mdi-plus"></i>
                  {t('BTN_ADD_DOMAIN')}
                </Button>
              </div>
            </div>
          </div>
        </Card.Header>

        {/* Table Body */}
        <Card.Body className="p-0">
          <div className="table-responsive">
            <Table className="mb-0" hover>
              <thead className="table-light">
                <tr>
                  <th className="text-center" style={{ width: '40px' }}>
                    <input
                      id="select_all"
                      type="checkbox"
                      className="form-check-input"
                      checked={clientWebsites.length > 0 && checkedList.length === clientWebsites.length}
                      onChange={(e) => onChangeSelectAllChecked && onChangeSelectAllChecked(e.target.checked)}
                    />
                  </th>
                  <th className="text-center" style={{ width: '80px' }}></th>
                  <th>{t('NAME_COL_WEBSITE_NAME')}</th>
                  <th>{t('NAME_COL_WEBSITE_DESCRIPTION')}</th>
                  <th>{t('NAME_COL_WEBSITE_AI_ENABLED')}</th>
                  <th className="text-center" style={{ width: '80px' }}>{t('NAME_COL_STATUS')}</th>
                  <th>{t('NAME_COL_CREATED_DATE')}</th>
                  <th>{t('NAME_COL_UPDATED_DATE')}</th>
                  <th className="text-center" style={{ width: '100px' }}>{t('NAME_COL_ACTIONS')}</th>
                </tr>
              </thead>

              <tbody>
                {clientWebsites.map((item, index) => renderWebsiteItem(item, index))}

                {clientWebsites.length === 0 && !isLoading && (
                  <tr>
                    <td colSpan="8" className="text-center py-5">
                      <div className="text-muted">
                        <i className="mdi mdi-web-off mdi-48px d-block mb-3 opacity-50"></i>
                        <h6 className="fw-normal">{t('NO_CLIENT_WEBSITES_FOUND')}</h6>
                        <p className="small mb-0">
                          {t('MSG_PLEASE_ADD_FIRST_CLIENT_WEBSITE')}
                        </p>
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
                <div className="mt-2 text-muted small">{t('MSG_DATA_CLIENT_WEBSITES_LOADING')}</div>
              </div>
            </div>
          )}
        </Card.Body>
      </Card>
    </div>
  );
};

export default ClientWebsitesTable;
