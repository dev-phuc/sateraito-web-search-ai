import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from "react-router";

// Zustand store
import useStoreApp from '@/store/app';
import useActiveMenuItem from '@/hooks/useActiveMenuItem';

// i18n
import { useTranslation } from "react-i18next";

// Ant Design
import {
  GlobalOutlined, HomeOutlined, DashboardFilled, BarChartOutlined,
  ProductOutlined, ContainerOutlined, ApartmentOutlined, ShopOutlined,
  DatabaseOutlined, ExperimentOutlined, UserOutlined
} from '@ant-design/icons';

import { Layout, Menu } from 'antd';
const { Sider } = Layout;

import LogoApp from '@/assets/logo_app.png';
import LogoAppFull from '@/assets/logo_app_full.svg';

const SiderApp = ({ isLoading, collapsed }) => {
  // Router
  const navigate = useNavigate();
  const location = useLocation();
  const { tenant, app_id } = useParams();

  // i18n
  const { t } = useTranslation();

  // State
  const [menuItems, setMenuItems] = useState([]);
  const [openKeys, setOpenKeys] = useState([]);
  
  // Custom hook for active menu item
  const activeKey = useActiveMenuItem(menuItems);

  // Zustand store
  const { sidebarClosed } = useStoreApp((state) => state);
  const { setSidebarClosed } = useStoreApp();

  // Classes - clsx
  const classes = {
    wrapLogo: 'flex items-center justify-center h-[69px] bg-white shadow-sm',
    logo: 'h-10',
    wrapMenu: 'h-full',
  };

  // Process func - No longer needed as we use the hook
  const processSetMenuItems = () => {
    // Define menu items
    let items = [];

    items = [
      {
        key: 'admin_dashboard',
        icon: <HomeOutlined />,
        pathname: `/${tenant}/${app_id}/admin_console`,
        label: t('TXT_DASHBOARD'),
      },
      {
        key: 'domains_management',
        icon: <GlobalOutlined />,
        pathname: `/${tenant}/${app_id}/admin_console/domains`,
        label: t('TXT_DOMAINS_MANAGEMENT'),
      },
      // Design search box
      {
        key: 'design_search_box',
        icon: <HomeOutlined />,
        pathname: `/${tenant}/${app_id}/admin_console/design-search-box`,
        label: t('TXT_DESIGN_SEARCH_BOX'),
      },
      // Encoder HTML/JavaScript of the search box
      {
        key: 'encoder_html_js',
        icon: <HomeOutlined />,
        pathname: `/${tenant}/${app_id}/admin_console/box-search-encoder`,
        label: t('TXT_ENCODER_HTML_JS'),
      },
      // Design banner keywords
      {
        key: 'design_banner',
        icon: <ProductOutlined />,
        pathname: `/${tenant}/${app_id}/admin_console/design-banner`,
        label: t('TXT_DESIGN_BANNER_KEYWORDS'),
      },
      // AI Configuration
      {
        key: 'ai_configuration',
        icon: <ExperimentOutlined />,
        pathname: `/${tenant}/${app_id}/admin_console/ai-configuration`,
        label: t('TXT_AI_CONFIGURATION'),
      },
      // Operations logs
      {
        key: 'operations_logs',
        icon: <ContainerOutlined />,
        pathname: `/${tenant}/${app_id}/admin_console/logs`,
        label: t('TXT_OPERATIONS_LOGS'),
      },
      // Usage statistics
      {
        key: 'usage_statistics',
        icon: <BarChartOutlined />,
        pathname: `/${tenant}/${app_id}/admin_console/usage`,
        label: t('TXT_USAGE_STATISTICS'),
      },
    ];

    // Set menu items
    setMenuItems(items);
  };

  // Handler func
  const handlerOnSelectMenuItem = (event) => {
    const { key, item } = event;
    const { pathname } = item.props;

    if (key && pathname) {
      navigate(pathname);
    }
  };

  const handleOpenChange = (keys) => {
    setOpenKeys(keys);
  };

  // Effect to set open keys based on active item
  useEffect(() => {
    if (activeKey && menuItems.length > 0) {
      // Find parent menu item if active item is a child
      const parentItem = menuItems.find(item => 
        item.children && item.children.some(child => child.key === activeKey)
      );
      
      if (parentItem && !openKeys.includes(parentItem.key)) {
        setOpenKeys(prev => [...prev, parentItem.key]);
      }
    }
  }, [activeKey, menuItems]);

  useEffect(() => {
    processSetMenuItems();
  }, []);

  useEffect(() => {
    // Get sidebar state from localStorage
    const storedSidebarClosed = localStorage.getItem('sidebarClosed');
    const isClosed = storedSidebarClosed === 'true' || storedSidebarClosed === null;
    setSidebarClosed(isClosed);
  }, []);

  return (
    <div className='h-full flex flex-col'>
      {/* Logo */}
      <div className={classes.wrapLogo}>
        <div className='flex items-center'>
          <img src={!sidebarClosed ? LogoAppFull : LogoApp} className='h-9' alt="Logo" />
        </div>
      </div>

      {/* Sider */}
      <div className="h-full bg-white overflow-y-auto overflow-x-hidden">
        {!isLoading && (
          <Sider collapsed={sidebarClosed} className={classes.wrapMenu} width={210} style={{ backgroundColor: '#fff' }}>
            <Menu
              selectedKeys={[activeKey]}
              openKeys={openKeys}
              onOpenChange={handleOpenChange}
              mode="inline" 
              items={menuItems} 
              onSelect={handlerOnSelectMenuItem}
            />
          </Sider>
        )}
      </div>
    </div>
  );
};


export default SiderApp;