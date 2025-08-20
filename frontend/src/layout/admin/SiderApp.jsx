import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from "react-router";

// Zustand store
import useStoreApp from '@/store/app';
import useActiveMenuItem from '@/hooks/useActiveMenuItem';

// i18n
import { useTranslation } from "react-i18next";

// Ant Design
import {
  AuditOutlined, TeamOutlined, HomeOutlined, DashboardFilled, BarChartOutlined,
  ProductOutlined, ContainerOutlined, ApartmentOutlined, ShopOutlined,
  DatabaseOutlined, ExperimentOutlined, UserOutlined
} from '@ant-design/icons';

import { Layout, Menu } from 'antd';
const { Sider } = Layout;

const SiderApp = ({ isLoading, collapsed }) => {
  // Router
  const navigate = useNavigate();
  const location = useLocation();
  const { storeCode } = useParams();
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
    wrapLogo: 'flex items-center justify-center h-16 bg-white shadow-sm',
    logo: 'h-10',
    wrapMenu: 'h-full',
  };

  // Process func - No longer needed as we use the hook
  const processSetMenuItems = () => {
    // Define menu items
    let items = [];

    if (storeCode) {
      items = [
        {
          key: 'admin_dashboard',
          icon: <HomeOutlined />,
          pathname: `/store/${storeCode}/admin`,
          label: t('TXT_DASHBOARD'),
        },
        {
          key: 'admin_product_types_management',
          icon: <ApartmentOutlined />,
          pathname: `/store/${storeCode}/admin/loai-san-pham`,
          label: t('TXT_PRODUCT_TYPES_MANAGEMENT'),
        },
        {
          key: 'admin_employee',
          icon: <TeamOutlined />,
          pathname: `/store/${storeCode}/admin/nhan-vien`,
          label: t('TXT_EMPLOYEE'),
        },
        {
          key: 'admin_supplier_management',
          pathname: `/store/${storeCode}/admin/nha-cung-cap`,
          icon: <BarChartOutlined />,
          label: t('TXT_SUPPLIERS'),
        },
        // {
        //   key: 'admin_cost_analysis',
        //   pathname: `/store/${storeCode}/admin/phan-tich-chi-phi`,
        //   icon: <DashboardFilled />,
        //   label: t('TXT_COST_ANALYSIS'),
        // },
        {
          key: 'admin_product_management',
          icon: <ProductOutlined />,
          pathname: `/store/${storeCode}/admin/san-pham`,
          label: t('TXT_PRODUCT_MANAGEMENT'),
        },
        {
          key: 'admin_composite_product_management',
          icon: <ProductOutlined />,
          pathname: `/store/${storeCode}/admin/san-pham-tong-hop`,
          label: t('TXT_COMPOSITE_PRODUCTS'),
        },
        {
          key: 'admin_ingredient_management',
          icon: <ProductOutlined />,
          pathname: `/store/${storeCode}/admin/nguyen-lieu`,
          label: t('TXT_INGREDIENTS'),
        },
        {
          key: 'admin_recipe_management',
          icon: <ExperimentOutlined />,
          pathname: `/store/${storeCode}/admin/cong-thuc`,
          label: t('TXT_RECIPES'),
        },
        {
          key: 'admin_product_recipe_management',
          icon: <DatabaseOutlined />,
          pathname: `/store/${storeCode}/admin/san-pham-cong-thuc`,
          label: t('TXT_PRODUCT_RECIPE_MANAGEMENT'),
        },
        {
          key: 'admin_warehouse_management',
          icon: <ContainerOutlined />,
          label: t('TXT_WAREHOUSE_MANAGEMENT'),
          children: [
            {
              key: 'admin_warehouse_list',
              pathname: `/store/${storeCode}/admin/kho`,
              label: t('TXT_WAREHOUSES'),
            },
            {
              key: 'admin_inventory_management',
              pathname: `/store/${storeCode}/admin/ton-kho`,
              label: t('TXT_INVENTORY_MANAGEMENT'),
            },
            {
              key: 'admin_ingredient_inventory',
              pathname: `/store/${storeCode}/admin/nguyen-lieu/ton-kho`,
              label: t('TXT_INGREDIENT_INVENTORY'),
            },
          ],
        },

        // {
        //   key: 'admin_employee',
        //   icon: <TeamOutlined />,
        //   label: t('TXT_EMPLOYEE'),
        //   children: [
        //     {
        //       key: 'admin_employee_manager',
        //       pathname: `/store/${storeCode}/admin/nhan-vien`,
        //       label: t('TXT_MANAGER'),
        //     },
        //     {
        //       key: 'admin_employee_skill_categorization',
        //       pathname: `/store/${storeCode}/admin/nhan-vien/phan-loai-ky-nang`,
        //       label: t('TXT_SKILL_CATEGORIZATION'),
        //     },
        //     {
        //       key: 'admin_employee_track_work_hours',
        //       pathname: `/store/${storeCode}/admin/nhan-vien/theo-doi-gio-lam`,
        //       label: t('TXT_TRACK_WORK_HOURS'),
        //     },
        //   ],
        // },

        // {
        //   key: 'admin_shift_optimization',
        //   icon: <DashboardFilled />,
        //   label: t('TXT_SHIFT_OPTIMIZATION'),
        //   children: [
        //     {
        //       key: 'admin_shift_scheduling',
        //       pathname: `/store/${storeCode}/admin/toi-uu-hoa-ca/sap-xep-ca`,
        //       label: t('TXT_SHIFT_SCHEDULING'),
        //     },
        //     {
        //       key: 'admin_shift_setup',
        //       pathname: `/store/${storeCode}/admin/toi-uu-hoa-ca/thiet-lap-ca`,
        //       label: t('TXT_SHIFT_SETUP'),
        //     },
        //   ],
        // },
        // {
        //   key: 'admin_revenue_forecast',
        //   icon: <AuditOutlined />,
        //   label: t('TXT_REVENUE_FORECAST'),
        //   children: [
        //     {
        //       key: 'admin_revenue_forecast_main',
        //       pathname: `/store/${storeCode}/admin/du-doan-doanh-thu`,
        //       label: t('TXT_REVENUE_FORECAST'),
        //     },
        //     {
        //       key: 'admin_historical_analysis',
        //       pathname: `/store/${storeCode}/admin/phan-tich-lich-su`,
        //       label: t('TXT_HISTORICAL_ANALYSIS'),
        //     },
        //   ],
        // },

        {
          key: 'go_to_sale_member_screen',
          icon: <ShopOutlined />,
          pathname: `/store/${storeCode}/sale`,
          label: t('TXT_GO_TO_SALE_MEMBER_SCREEN'),
        },
      ];
    }

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
  }, [storeCode, t]);

  useEffect(() => {
    // Get sidebar state from localStorage
    const storedSidebarClosed = localStorage.getItem('sidebarClosed');
    const isClosed = storedSidebarClosed === 'true' || storedSidebarClosed === null;
    setSidebarClosed(isClosed);
  }, []);

  return (
    <div className='h-full'>
      {/* Logo */}
      <div className={classes.wrapLogo}>
        <div className='flex items-center cursor-pointer' onClick={() => navigate('/overview')}>
          <img src="/favicon.ico" className='h-10' alt="Logo" />
          {!sidebarClosed &&
            (
              <span className='app-name text-lg font-bold ml-2'>{t('TXT_COMPANY_NAME')}</span>
            )
          }
        </div>
      </div>

      {/* Sider */}
      <Sider collapsed={sidebarClosed} className={classes.wrapMenu} width={210} style={{ backgroundColor: '#fff' }}>
        <div className='overflow-y-auto h-full'>
          {!isLoading &&
            <Menu 
              selectedKeys={[activeKey]}
              openKeys={openKeys}
              onOpenChange={handleOpenChange}
              mode="inline" 
              items={menuItems} 
              onSelect={handlerOnSelectMenuItem}
            />
          }
        </div>
      </Sider>
    </div>
  );
};


export default SiderApp;