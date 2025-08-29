
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router';
import { Outlet } from 'react-router';

import { useTranslation } from "react-i18next";

import { LoadingOutlined } from '@ant-design/icons';

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

  // Use hooks state
  const { user, isChecking } = useAuth();

  // Params

  // State

  // Effect
  useEffect(() => {
  }, []);

  if (isChecking) {
    return (
      <div className="w-full h-screen flex items-center justify-center">
        <LoadingOutlined style={{ fontSize: 40 }} spin />
      </div>
    );
  }

  return (
    <Layout className='h-screen'>

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