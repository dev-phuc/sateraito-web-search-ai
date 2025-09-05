
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router';
import { Outlet } from 'react-router';

import { useTranslation } from "react-i18next";

import { LoadingOutlined } from '@ant-design/icons';
import { message } from 'antd';

// Hook components
import useAuth from "@/hooks/useAuth";

import { Layout } from 'antd';
const { Content } = Layout;

// Zustand store
import useStoreApp from '@/store/app';

// Request

import SiderApp from './SiderApp';
import HeaderApp from './HeaderApp';

const LayoutApp = () => {
  // I18n
  const { t } = useTranslation();

  // Ant
  const [messageApi, contextHolder] = message.useMessage();

  // Use hooks state
  const { user, isChecking } = useAuth();

  // Zustand store
  const { messageNotify, setMessageNotify } = useStoreApp();

  // Params

  // State

  // Effect
  useEffect(() => {
  }, []);

  useEffect(() => {
    if (messageNotify) {
      const { type, text } = messageNotify;
      
      switch (type) {
        case 'success':
          messageApi.success(t(text));
          break;
        case 'warning':
          messageApi.warning(t(text));
          break;
        case 'info':
          messageApi.info(t(text));
          break;
        case 'error':
        default:
          messageApi.error(t(text));
          break;
      }

      setMessageNotify(null);
    }
  }, [messageNotify]);

  if (isChecking) {
    return (
      <div className="w-full h-screen flex items-center justify-center">
        <LoadingOutlined style={{ fontSize: 40 }} spin />
      </div>
    );
  }

  return (
    <Layout className='h-screen'>
      {contextHolder}

      {/* Sider */}
      <SiderApp isLoading={isChecking} />

      <Layout>

        {/* Header */}
        <HeaderApp isLoading={isChecking} />

        {/* Content */}
        <Content className='my-layout-content'>
          < Outlet />
        </Content>

      </Layout>
    </Layout>
  );
};
export default LayoutApp;