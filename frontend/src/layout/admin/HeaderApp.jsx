import React, { useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router';
import { useTranslation } from 'react-i18next';

// Hook components
import useAuth from "@/hooks/useAuth";
import AdminBreadcrumb from "@/components/Breadcrumb/AdminBreadcrumb";

// Ant Design
import { LoadingOutlined, BellOutlined, ArrowLeftOutlined, LeftOutlined, RightOutlined, UserOutlined, HomeOutlined } from '@ant-design/icons';
import { Layout, Button, Dropdown, Badge, message, Avatar } from 'antd';
const { Header } = Layout;

// Zustand store
import useStoreStore from '@/store/store';
import useStoreApp from '@/store/app';

// Request

const HeaderApp = ({ }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const params = useParams();
  const storeCode = params.storeCode;

  // Ant Design message
  const [messageApi, contextHolder] = message.useMessage();

  // Use i18n
  const { t } = useTranslation();

  // Hook components
  const { user, isChecking, signOut } = useAuth();

  // Zustand store
  const { isLoading, stores, fetchStores } = useStoreStore();
  const { sidebarClosed } = useStoreApp((state) => state);
  const { toggleSidebar, closeSidebar } = useStoreApp();
  const { isFetchingStoreActiveError, messageStoreActiveError } = useStoreApp();

  // State
  const [storeActive, setStoreActive] = React.useState(null);

  // Handler
  const handleCollapse = () => {
    toggleSidebar();
  };
  const handlerOnSelectMenuItem = async () => {
    try {
      await signOut();
    } catch (error) {
      let msgError = t(error);
      if (msgError == error) {
        msgError = t('TXT_SIGN_OUT_ERROR');
      }
      messageApi.error(msgError);
    }
  };
  const handleSelectStore = (store) => {
    setStoreActive(store);

    let url = window.location.pathname;
    const match = url.match(/\/store\/[a-zA-Z0-9-]+\/(.*)/);
    const after = match ? match[1] : '';

    let nextUrl = '';
    if (after) {
      nextUrl = `/store/${store.storeCode}/${after}`;
    } else {
      nextUrl = `/store/${store.storeCode}/admin`;
    }

    navigate(nextUrl);
  };

  // Constants
  const items = [
    {
      label: (
        <span>
          <UserOutlined style={{ marginRight: '8px' }} />
          Quản lý Profile
        </span>
      ),
      key: 'profile',
      onClick: () => {
        navigate('/profile');
      },
    },
    {
      type: 'divider',
    },
    {
      label: (<span>Đăng Xuất</span>),
      key: '0',
      onClick: handlerOnSelectMenuItem,
    },
  ];
  const data_notification_example = [
    {
      id: 1,
      title: 'Thông báo 1',
      description: 'Mô tả thông báo 1',
      time: '2023-10-01 12:00',
    },
    {
      id: 2,
      title: 'Thông báo 2',
      description: 'Mô tả thông báo 2',
      time: '2023-10-01 13:00',
    },
    {
      id: 3,
      title: 'Thông báo 3',
      description: 'Mô tả thông báo 3',
      time: '2023-10-01 14:00',
    },
    {
      id: 4,
      title: 'Thông báo 4',
      description: 'Mô tả thông báo 4',
      time: '2023-10-01 15:00',
    },
  ]

  useEffect(() => {
    if (!isLoading) {
      fetchStores();
    }
  }, []);

  useEffect(() => {
    if (!isLoading) {
      const storeSelected = stores.find(store => store.storeCode === storeCode);
      if (storeSelected) {
        setStoreActive(storeSelected);
      } else {
        if (isFetchingStoreActiveError) {
          setStoreActive(null);

          if (messageStoreActiveError) {
            messageApi.error(messageStoreActiveError);
          }

          navigate('/overview');
        }
      }
    }
  }, [storeCode, stores]);

  return (
    <>
      <Header className='shadow' style={{ backgroundColor: '#fff', paddingLeft: 10, paddingRight: 20 }}>
        {contextHolder}
        <div className='flex items-center justify-between h-full'>

          <div className='flex items-center justify-end gap-3'>
            {/* Collapse button */}
            <Button
              type='text'
              shape="circle"
              icon={!sidebarClosed ? <LeftOutlined /> : <RightOutlined />}
              onClick={handleCollapse}
              className='border-none text-gray-500 hover:text-gray-700'
            />

            {/* Store selection dropdown */}
            <Dropdown
              menu={{
                items: stores.map(store => ({
                  key: store.code,
                  label: (
                    <div className='flex items-center gap-2 cursor-pointer hover:bg-gray-100 px-2 py-1'>
                      <img src={store.imageUrl} className='h-full object-cover rounded-full' style={{ width: 18, height: 18 }} />
                      {store.name}
                    </div>
                  ),
                  onClick: () => handleSelectStore(store),
                })),
              }}
              trigger={['click']}
            >
              <div className='h-10 flex items-center justify-start cursor-pointer border border-gray-200 rounded-lg hover:bg-gray-100 px-2'>
                {storeActive && (
                  <img src={storeActive.imageUrl} alt="Store Logo" className='h-full object-cover rounded-full' style={{ width: 25, height: 25 }} />
                )}
                <div className='h-full ml-2 flex items-center justify-center'>
                  {storeActive ? storeActive.name : 'Chọn cửa hàng'}
                </div>
              </div>
            </Dropdown>
          </div>

          <div className='flex items-center justify-end gap-3'>

          {/* List notification */}
          <Dropdown
            menu={{
              items: data_notification_example.map(item => ({
                key: item.id,
                label: (
                  <div className='px-2 hover:bg-gray-100 cursor-pointer w-[250px]'>
                    <strong>{item.title}</strong>
                    <p>{item.description}</p>
                    <span className='text-gray-500'>{item.time}</span>
                  </div>
                ),
              })),
            }}
            trigger={['click']}
          >
            <Badge count={5}>
              <Button type='text' className='border-none text-gray-500 hover:text-gray-700'
                icon={<BellOutlined />}
              />
            </Badge>
          </Dropdown>

          {!isChecking ?
            (
              <Dropdown menu={{ items }} trigger={['click']}>
                <div className='h-10 flex items-center justify-center cursor-pointer border border-gray-200 rounded-lg hover:bg-gray-100 pt-1 px-2 ml-2'>
                  <span className='mr-3'>{user.displayName}</span>
                  <Avatar
                    size={25}
                    src={user.avatar}
                    icon={<UserOutlined />}
                    style={{
                      border: '4px solid #f0f0f0',
                      boxShadow: '0 4px 16px rgba(0,0,0,0.1)'
                    }}
                  />
                </div>
              </Dropdown>
            )
            :
            <LoadingOutlined style={{ fontSize: 24 }} spin />
          }
        </div>

      </div>
      </Header>
      
      {/* Breadcrumb */}
      <AdminBreadcrumb storeActive={storeActive} />
    </>
  );
};


export default HeaderApp;