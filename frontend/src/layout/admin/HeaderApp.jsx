import React, { useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router';
import { useTranslation } from 'react-i18next';

// Hook components
import useAuth from "@/hooks/useAuth";

// Ant Design
import { LoadingOutlined, BellOutlined, LeftOutlined, RightOutlined, UserOutlined, LogoutOutlined } from '@ant-design/icons';
import { Layout, Button, Dropdown, Badge, Avatar } from 'antd';
const { Header } = Layout;

// Zustand store
import useStoreApp from '@/store/app';

// Request

const HeaderApp = ({ }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const params = useParams();

  const { tenant, app_id } = params;

  // Use i18n
  const { t } = useTranslation();

  // Hook components
  const { user, userInfo, isChecking, signOut } = useAuth();

  // Zustand store
  const { sidebarClosed } = useStoreApp((state) => state);
  const { toggleSidebar, closeSidebar } = useStoreApp();

  // State

  // Handler
  const handleCollapse = () => {
    toggleSidebar();
  };
  const handlerOnSelectMenuItem = async () => {
    await signOut(tenant, app_id);
  };

  // Constants
  const items = [
    // {
    //   label: (
    //     <span>
    //       <UserOutlined style={{ marginRight: '8px' }} />
    //       Quản lý Profile
    //     </span>
    //   ),
    //   key: 'profile',
    //   onClick: () => {
    //     navigate('/profile');
    //   },
    // },
    // {
    //   type: 'divider',
    // },
    {
      label: (<span>{t('TXT_LOGOUT')}</span>),
      key: '0',
      onClick: handlerOnSelectMenuItem,
      icon: <LogoutOutlined style={{ marginRight: '8px' }} />
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

  return (
    <>
      <Header className='shadow' style={{ backgroundColor: '#fff', paddingLeft: 10, paddingRight: 20 }}>
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

          {!isChecking && userInfo ?
            (
              <Dropdown menu={{ items }} trigger={['click']}>
                <div className='h-10 flex items-center justify-center cursor-pointer border border-gray-200 rounded-lg hover:bg-gray-100 pt-1 px-2 ml-2'>
                  <span className='mr-3'>{userInfo.family_name}</span>
                  <Avatar
                    size={25}
                    src={userInfo.photo_url}
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
    </>
  );
};


export default HeaderApp;