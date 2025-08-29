import React, { useState } from 'react';

import { Form, Input, Button, message, Progress, Typography, Alert } from "antd";
import { LockOutlined, EyeInvisibleOutlined, EyeTwoTone } from '@ant-design/icons';

const { Text } = Typography;

// i18n
import { useTranslation } from 'react-i18next';

// Hook components
import useAuth from "@/hooks/useAuth";

import GoogleIcon from "@/assets/images/google-icon.png";
import BackgroundLogin from "@/assets/images/background-page-login.png";
import Logo from "@/assets/favicon.ico";

const LoginPage = () => {
  // Use hooks state
  const { isAuthenticated, isChecking, loginWithGoogle, loadProfile } = useAuth();
  
  // i18n
  const { t } = useTranslation();

  // Message API for notifications
  const [messageApi, contextHolder] = message.useMessage();

  // State
  const [isLoadingGoogle, setIsLoadingGoogle] = useState(false);

  const handlerLoginWithGoogle = async (event) => {
    event.preventDefault();

    // Set loading state for Google login
    setIsLoadingGoogle(true);

    // Call signInWithGoogle function from auth provider
    loginWithGoogle();
  };

  return (
    <div className={`flex flex-col items-center justify-center h-screen bg-cover bg-center`}
      style={{ backgroundImage: `url(${BackgroundLogin})` }}
    >
      {contextHolder}

      {/* Card container login */}
      {!isChecking && !isAuthenticated && (
        <div className="flex flex-col items-center justify-between bg-white shadow-md rounded-lg p-8 w-96">

          {/* Header */}
          <div className="flex items-center justify-center flex-col">

            {/* Logo */}
            <div className='flex items-center justify-center mb-4 w-24 h-24 p-3 rounded-full overflow-hidden shadow-md bg-white'>
              <img src={Logo} alt="Logo" className="w-full h-full object-cover" />
            </div>
            {/* Title and description */}
            <h1 className="text-2xl font-bold">
              {t('TXT_APP_NAME')}
            </h1>
            <p className="text-gray-600 mb-6">
              {t('TXT_APP_DESCRIPTION')}
            </p>
          </div>

          {/* Title and description */}
          <div className="content h-20 flex items-center justify-center flex-col">
            <Button className="flex items-center" 
              disabled={isLoadingGoogle} 
              loading={isLoadingGoogle}
              onClick={handlerLoginWithGoogle}
              style={{
                height: 45
              }}
            >
              {!isLoadingGoogle && <img src={GoogleIcon} alt="Google" className="w-8 h-8" />}
              <span className="ml-2">
                {t('TXT_LOGIN_WITH_GOOGLE')}
              </span>
            </Button>
          </div>

        </div>
      )}

    </div>
  );
};

export default LoginPage;