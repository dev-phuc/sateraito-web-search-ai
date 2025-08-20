import React, { useState } from 'react';

import { Form, Input, Button, message, Progress, Typography, Alert } from "antd";
import { LockOutlined, EyeInvisibleOutlined, EyeTwoTone } from '@ant-design/icons';

const { Text } = Typography;

// i18n
import { useTranslation } from 'react-i18next';

import GoogleIcon from "@/assets/images/google-icon.png";

// Hook components
import useAuth from "@/hooks/useAuth";

import Logo from "@/assets/favicon.ico";

// Request module
import { registerUser, loginWithUsername } from "@/request/auth";
import { DOMAIN_EMAIL_DEFAULT } from '@/constant';

const LoginPage = () => {
  // Use hooks state
  const { isAuthenticated, isChecking, loginWithGoogle, loadProfile } = useAuth();
  
  // i18n
  const { t } = useTranslation();

  // Message API for notifications
  const [messageApi, contextHolder] = message.useMessage();

  // State
  const [isShowFormRegister, setIsShowFormRegister] = useState(false);
  const [isLoadingGoogle, setIsLoadingGoogle] = useState(false);
  const [isLoadingUsernamePassword, setIsLoadingUsernamePassword] = useState(false);
  const [isLoadingRegister, setIsLoadingRegister] = useState(false);
  const [registerPassword, setRegisterPassword] = useState('');
  const [showPasswordRequirements, setShowPasswordRequirements] = useState(false);

  // Password strength functions
  const getPasswordStrength = (pwd) => {
    let score = 0;
    if (!pwd) return score;

    // Length check
    if (pwd.length >= 6) score += 40;
    if (pwd.length >= 8) score += 20;

    // Character variety checks
    if (/[a-zA-Z]/.test(pwd)) score += 20;
    if (/[0-9]/.test(pwd)) score += 20;

    return Math.min(score, 100);
  };

  const getPasswordStrengthText = (score) => {
    if (score < 40) return { text: t('TXT_PASSWORD_WEAK'), color: '#ff4d4f' };
    if (score < 80) return { text: t('TXT_PASSWORD_GOOD'), color: '#faad14' };
    return { text: t('TXT_PASSWORD_STRONG'), color: '#52c41a' };
  };

  const handlerLoginWithGoogle = async (event) => {
    event.preventDefault();

    // Set loading state for Google login
    setIsLoadingGoogle(true);

    // Call signInWithGoogle function from auth provider
    loginWithGoogle();
  };

  const handlerLoginWithUsernamePassword = async (data) => {
    setIsLoadingUsernamePassword(true);

    try {
      await loginWithUsername(data);
      loadProfile();
      messageApi.success(t('MSG_LOGIN_SUCCESS'));
    } catch (error) {
      messageApi.error(t('MSG_LOGIN_FAILED'));
      console.error('Login failed:', error);
    }

    setIsLoadingUsernamePassword(false);
  };

  const handlerShowFormRegister = () => {
    setIsShowFormRegister(true);
    setRegisterPassword(''); // Reset password state
    setShowPasswordRequirements(false); // Reset password requirements visibility
  };
  const handlerHideFormRegister = () => {
    setIsShowFormRegister(false);
    setRegisterPassword(''); // Reset password state
    setShowPasswordRequirements(false); // Reset password requirements visibility
  };
  const handlerSubmitFormRegister = async (form) => {
    setIsLoadingRegister(true);

    try {
      await registerUser(form);
      messageApi.success(t('MSG_REGISTER_SUCCESS'));
      setIsShowFormRegister(false);
      setRegisterPassword(''); // Reset password state
      setShowPasswordRequirements(false); // Reset password requirements visibility
    } catch (error) {
      messageApi.error(t('MSG_REGISTER_FAILED'));
    }

    setIsLoadingRegister(false);
  };

  return (
    <div className={`flex flex-col items-center justify-center h-screen`}>
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
              disabled={isLoadingGoogle || isLoadingUsernamePassword || isLoadingRegister} 
              loading={isLoadingGoogle}
              onClick={handlerLoginWithGoogle}
              style={{
                height: 45
              }}
            >
              {!isLoadingGoogle && <img src={GoogleIcon} alt="Google" className="w-8 h-8" />}
              <span className="ml-2">
                {isShowFormRegister ? t('TXT_REGISTER_WITH_GOOGLE') : t('TXT_LOGIN_WITH_GOOGLE')}
              </span>
            </Button>
          </div>

          <div className="flex justify-between items-center w-full my-4">
            {/* Line */}
            <div className="w-full border-t border-gray-300"></div>

            {/* Or */} 
            <p className="text-gray-500 mx-2 text-sm"> {t('TXT_OR')} </p>

            {/* Line */}
            <div className="w-full border-t border-gray-300"></div>
          </div>

          {/* Login by username password */}
          {!isShowFormRegister && (
            <Form name="login" className="w-full flex flex-col items-center justify-center mt-5"
              autoComplete="off"
              initialValues={{ remember: true }}
              onFinish={handlerLoginWithUsernamePassword}
            >
              
              <Form.Item name="username" rules={[
                { required: true, message: t('MSG_USERNAME_IS_REQUIRED') }
              ]} 
                className="w-full"
                style={{ marginBottom: '10px' }}
              >
                <Input type="text" placeholder={t('TXT_USERNAME')}/>
              </Form.Item>

              <Form.Item name="password" rules={[{ required: true, message: t('MSG_PASSWORD_IS_REQUIRED') }]}
                className="w-full"
              >
                <Input.Password placeholder={t('TXT_PASSWORD')} />
              </Form.Item>

              <Form.Item shouldUpdate 
                style={{ marginTop: '10px' }}
              >
                <Button type="primary" htmlType="submit" className="w-full" 
                  disabled={isLoadingGoogle || isLoadingUsernamePassword || isLoadingRegister} 
                  loading={isLoadingUsernamePassword}
                  style={{
                    height: 45
                  }}
                >
                  {t('TXT_LOGIN')}
                </Button>
              </Form.Item>

              <p className="text-gray-500 text-sm mt-8">
                {t('TXT_DONT_HAVE_ACCOUNT')}
                <span className="ml-1 text-blue-500 hover:underline cursor-pointer" onClick={handlerShowFormRegister}>
                  {t('TXT_REGISTER')}
                </span>
              </p>

            </Form>
          )}
          {isShowFormRegister && (
            <div className="w-full flex flex-col items-center justify-center">

              <h2 className="text-xl font-semibold mb-4">
                {t('TXT_CREATE_ACCOUNT')}
              </h2>

              {/* Password Requirements Alert - Only show when there's validation error */}
              {showPasswordRequirements && (
                <Alert
                  message={t('TXT_PASSWORD_REQUIREMENTS')}
                  description={
                    <div style={{ marginTop: '8px' }}>
                      <ul style={{ margin: '8px 0 0 0', paddingLeft: '20px', fontSize: '12px' }}>
                        <li>{t('TXT_PASSWORD_REQUIREMENT_LENGTH')}</li>
                        <li>{t('TXT_PASSWORD_REQUIREMENT_PATTERN')}</li>
                      </ul>
                    </div>
                  }
                  type="warning"
                  showIcon
                  style={{ marginBottom: '20px', borderRadius: '8px' }}
                />
              )}

              <Form name="register" className="w-full flex flex-col items-center justify-center mt-5"
                autoComplete="off"
                initialValues={{ remember: true }}
                onFinish={handlerSubmitFormRegister}
                onFinishFailed={() => {
                  // Show password requirements when form validation fails
                  setShowPasswordRequirements(true);
                }}
              >
                {/* Username */}
                <Form.Item name="username" rules={[
                  { required: true, message: t('MSG_USERNAME_IS_REQUIRED') },
                  ({ getFieldValue }) => ({ validator(_, value) {
                    let regex = /^[a-zA-Z0-9._-]+$/;
                    if (!value || regex.test(value)) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error(t('MSG_USERNAME_INVALID')));
                    },
                  }),
                ]}
                  className="w-full"
                >
                  <Input type="text" placeholder={t('TXT_USERNAME')} />
                </Form.Item>

                {/* Password */}
                <Form.Item name="password" rules={[
                  { required: true, message: t('MSG_PASSWORD_IS_REQUIRED') },
                  { min: 6, message: t('MSG_PASSWORD_MIN_LENGTH') },
                  {
                    pattern: /^(?=.*[a-zA-Z])(?=.*\d)/,
                    message: t('MSG_PASSWORD_PATTERN')
                  }
                ]}
                  className="w-full"
                  style={{ marginTop: '10px' }}
                >
                  <Input.Password 
                    prefix={<LockOutlined style={{ color: '#bfbfbf' }} />}
                    placeholder={t('TXT_PASSWORD')}
                    onChange={(e) => setRegisterPassword(e.target.value)}
                    iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
                    style={{ borderRadius: '8px' }}
                  />
                </Form.Item>

                {/* Password Strength Indicator */}
                {registerPassword && (
                  <div style={{ width: '100%', marginBottom: '10px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <Text type="secondary" style={{ fontSize: '12px' }}>{t('TXT_PASSWORD_STRENGTH')}</Text>
                      <Text style={{ 
                        color: getPasswordStrengthText(getPasswordStrength(registerPassword)).color, 
                        fontWeight: 'bold', 
                        fontSize: '12px' 
                      }}>
                        {getPasswordStrengthText(getPasswordStrength(registerPassword)).text}
                      </Text>
                    </div>
                    <Progress 
                      percent={getPasswordStrength(registerPassword)} 
                      strokeColor={getPasswordStrengthText(getPasswordStrength(registerPassword)).color}
                      showInfo={false}
                      size="small"
                      style={{ height: '6px' }}
                    />
                  </div>
                )}

                {/* Confirm password */}
                <Form.Item name="confirmPassword" dependencies={['password']} 
                  rules={[
                    { required: true, message: t('MSG_CONFIRM_PASSWORD_IS_REQUIRED') },
                    ({ getFieldValue }) => ({ validator(_, value) {
                        if (!value || getFieldValue('password') === value) {
                          return Promise.resolve();
                        }
                        return Promise.reject(new Error(t('MSG_PASSWORD_MISMATCH')));
                      },
                    }),
                  ]}
                  style={{ marginTop: '10px' }}
                  className="w-full"
                >
                  <Input.Password 
                    prefix={<LockOutlined style={{ color: '#bfbfbf' }} />}
                    placeholder={t('TXT_CONFIRM_PASSWORD')}
                    iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
                    style={{ borderRadius: '8px' }}
                  />
                </Form.Item>

                {/* Fullname */}
                <Form.Item name="fullname" rules={[{ required: true, message: t('MSG_FULLNAME_IS_REQUIRED') }]}
                  className="w-full"
                  style={{ marginTop: '10px' }}
                >
                  <Input type="text" placeholder={t('TXT_FULLNAME')} />
                </Form.Item>

                {/* email */}
                <Form.Item name="email" rules={[
                  { type: 'email', message: t('MSG_EMAIL_INVALID') },
                ]}
                  className="w-full"
                  style={{ marginTop: '10px' }}
                >
                  <Input type="email" placeholder={t('TXT_EMAIL')} />
                </Form.Item>

                <Form.Item shouldUpdate 
                  style={{ marginTop: '10px' }}
                >
                  <Button type="primary" htmlType="submit" className="w-full"
                    disabled={isLoadingGoogle || isLoadingUsernamePassword || isLoadingRegister}
                    loading={isLoadingRegister}
                    style={{
                      height: 45
                    }}
                  >
                    {t('TXT_REGISTER')}
                  </Button>
                </Form.Item>
              </Form>

              <p className="text-gray-500 text-sm mt-8">
                {t('TXT_ALREADY_HAVE_ACCOUNT')}
                <span className="ml-1 text-blue-500 hover:underline cursor-pointer" onClick={handlerHideFormRegister}>
                  {t('TXT_BACK_TO_LOGIN')}
                </span>
              </p>
            </div>
          )}

        </div>
      )}

    </div>
  );
};

export default LoginPage;