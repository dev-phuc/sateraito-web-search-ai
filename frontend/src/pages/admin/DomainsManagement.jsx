import { useRef, useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';

// Ant Design components
// import {  } from 'antd';

// Custom components
// import { } from '@/components';

const DomainsManagement = () => {
  // Default hooks
  const navigate = useNavigate();
  const { t } = useTranslation();

  // States
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
  }, []);

  // Return the component
  return (
    <>
      <h1>{t('TXT_DOMAINS_MANAGEMENT')}</h1>
    </>
  );
};

export default DomainsManagement;
