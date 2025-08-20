
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router';
import { Outlet } from 'react-router';

import { useTranslation } from "react-i18next";

// Hook components
import useAuth from "@/hooks/useAuth";

import { Layout } from 'antd';
const { Content } = Layout;

// Zustand store
import useStoreApp from '@/store/app';

// Request
import { getMyStoreByCode, validateStoreCode } from '@/request/store';

import SiderApp from './SiderApp';
import HeaderApp from './HeaderApp';

const LayoutApp = () => {
  // I18n
  const { t } = useTranslation();

  // Use hooks state
  const { user } = useAuth();

  // Params
  const { storeCode } = useParams();

  // Zustand store
  const { setStoreActive, clearStoreActive,
    setStoreActiveIsLoading, setIsFetchingStoreActiveError, setMessageStoreActiveError
  } = useStoreApp();

  // State
  const [isLoading, setIsLoading] = useState(true);

  const handlerLoadStore = async () => {
    clearStoreActive();
    setStoreActiveIsLoading(true);
    setIsFetchingStoreActiveError(false);
    setMessageStoreActiveError('');

    try {
      const store = await getMyStoreByCode(storeCode);
      setStoreActive(store);
    } catch (error) {
      setIsFetchingStoreActiveError(true);
      let msgError = t(error);
      if (msgError == error) msgError = t('TXT_STORE_NOT_FOUND');
      setMessageStoreActiveError(msgError);
      console.error('Failed to load store:', msgError);
    } finally {
      setStoreActiveIsLoading(false);
      setIsLoading(false);
    }
  };

  // Effect
  useEffect(() => {
    if (user && user.id) {
      setIsLoading(false);
    }
  }, [user]);

  useEffect(() => {
    handlerLoadStore();
  }, [storeCode]);

  return (
    <Layout className='h-screen'>

      {/* Sider */}
      <SiderApp isLoading={isLoading} />

      <Layout>

        {/* Header */}
        <HeaderApp isLoading={isLoading} />

        {/* Content */}
        <Content className='my-layout-content'>

          {/* This is where the child routes will be rendered */}
          {!isLoading && <Outlet />}

        </Content>

      </Layout>
    </Layout>
  );
};
export default LayoutApp;