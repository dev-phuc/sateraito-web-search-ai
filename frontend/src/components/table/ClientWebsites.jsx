import { useRef, useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router';

// Ant Design components
import { Table, Tag, Switch, Avatar, Button, Tooltip, Popconfirm } from 'antd';
import { EditOutlined, DeleteOutlined } from '@ant-design/icons';

// Custom components
// import { } from '@/components';

// Zustand
import useStoreClientWebsites from '@/store/client_websites';

const ClientWebsitesTable = ({ tenant, app_id, onSelectEdit, onSubmitDelete }) => {
  // Default hooks
  const navigate = useNavigate();
  const { t } = useTranslation();

  // Zustand stores
  const { isLoading, clientWebsites } = useStoreClientWebsites();

  // States

  // 
  const columns = [
    {
      dataIndex: 'favicon_url',
      key: 'favicon_url',
      render: (url, record) =>
        <Avatar src={url} alt={record.domain} shape="square" />,
      width: 50,
    },
    {
      title: t('LABEL_DOMAIN'),
      dataIndex: 'domain',
      key: 'domain',
      render: (domain, record) => (
        <a href={domain} target="_blank" rel="noopener noreferrer">
          {domain}
        </a>
      ),
    },
    {
      title: t('LABEL_SITE_NAME'),
      dataIndex: 'site_name',
      key: 'site_name',
      width: 150,
      render: (text) => (
        <Tooltip title={text}>
          <div className="whitespace-nowrap w-[200px] overflow-hidden text-ellipsis">{text}</div>
        </Tooltip>
      ),
    },
    {
      title: t('LABEL_DESCRIPTION'),
      dataIndex: 'description',
      key: 'description',
      width: 150,
      render: (text) => (
        <Tooltip title={text}>
          <div className="whitespace-nowrap w-[200px] overflow-hidden text-ellipsis">{text}</div>
        </Tooltip>
      ),
    },
    {
      title: t('LABEL_AI_ENABLED'),
      dataIndex: 'ai_enabled',
      key: 'ai_enabled',
      render: (enabled) => (
        <Switch checked={enabled} disabled />
      ),
      width: 120,
    },
    {
      title: t('LABEL_STATUS'),
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === 'active' ? 'green' : 'red'}>
          {t(`STATUS_${status.toUpperCase()}`)}
        </Tag>
      ),
      width: 120,
    },
    {
      title: t('LABEL_CREATED_DATE'),
      dataIndex: 'created_date',
      key: 'created_date',
      render: (date) => (
        <Tooltip title={date}>
          <span>{date?.slice(0, 10)}</span>
        </Tooltip>
      ),
      width: 150,
    },
    {
      title: t('LABEL_UPDATED_DATE'),
      dataIndex: 'updated_date',
      key: 'updated_date',
      render: (date) => (
        <Tooltip title={date}>
          <span>{date?.slice(0, 10)}</span>
        </Tooltip>
      ),
      width: 150,
    },
    {
      key: 'actions',
      render: (_, record) => (
        <div className="flex space-x-2">
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => onSelectEdit(record)}
          >
            {t('BTN_EDIT')}
          </Button>
          <Popconfirm 
            title={t('CONFIRM_DELETE_CLIENT_WEBSITE')}
            okText={t('BTN_YES')}
            cancelText={t('BTN_NO')}
            onConfirm={() => onSubmitDelete(record)}
          >
            <Button
              type="link"
              icon={<DeleteOutlined />}
              danger
            >
              {t('BTN_DELETE')}
            </Button>
          </Popconfirm>
        </div>
      ),
      width: 100,
    },
  ];

  // Return the component
  return (
    <div className="h-full wrapper bg-white m-4 mt-0 rounded-lg shadow-md">
      <Table
        rowKey="id"
        columns={columns}
        dataSource={clientWebsites}
        loading={isLoading}
        pagination={{ pageSize: 10 }}
        scroll={{ x: true }}
      />
    </div>
  );
};

export default ClientWebsitesTable;
