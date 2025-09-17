import { useEffect, useReducer, useState } from "react";
import { useTranslation } from "react-i18next";
import { useParams, useNavigate } from "react-router";

import AuthContext from "@/contexts/JWTContext";

import { getMe, logout, openPopupLoginWithGoogle } from '@/request/auth';

import i18n from "@/locales";
import { LANGUAGE_SUPPORTED } from "@/constants";
import { LANGUAGE_DEFAULT } from '@/constants';


const SET_TENANT_APP_ID = "SET_TENANT_APP_ID";
const INITIALIZE = "INITIALIZE";
const SET_LOADING = "SET_LOADING";
const SIGN_IN = "SIGN_IN";
const SIGN_OUT = "SIGN_OUT";
const IS_CHECKING = "IS_CHECKING";
const IS_ERROR = "IS_ERROR";

const initialState = {
  tenant: null,
  app_id: null,

  isAuthenticated: false,
  isInitialized: false,
  user: null,
  userInfo: null,

  isChecking: true,
  isError: false,
  errorMessage: '',
};

const JWTReducer = (state, action) => {
  switch (action.type) {
    case SET_TENANT_APP_ID:
      return {  ...state, tenant: action.payload.tenant, app_id: action.payload.app_id };
    case INITIALIZE:
      const { isAuthenticated, user } = action.payload;
      return {
        ...state,
        user,
        isAuthenticated,
        isInitialized: true,
        userInfo: user ? user.user_info : null,
      };
    case SET_LOADING:
      return {
        ...state,
        isChecking: action.payload,
      };
    case SIGN_IN:
      return {
        ...state,
        isAuthenticated: true,
        user: action.payload.user,
      };
    case SIGN_OUT:
      return {
        ...state,
        isAuthenticated: false,
        isInitialized: false,
        user: null,
        userInfo: null,
        isChecking: false,
        isError: false,
        errorMessage: '',
      };
    case IS_CHECKING:
      return {
        ...state,
        isChecking: action.payload.isChecking,
      };
    case IS_ERROR:
      return {
        ...state,
        isError: action.payload.isError,
        errorMessage: action.payload.errorMessage,
      };
    default:
      return {
        ...state,
        isInitialized: true,
        isAuthenticated: false,
        user: null,
        isChecking: false,
        isError: false,
        errorMessage: '',
      };
  }
};

function AuthProvider({ children }) {
  const { i18n, t } = useTranslation();
  const navigate = useNavigate();

  const [state, dispatch] = useReducer(JWTReducer, initialState);
  let pageLoginUrl = `/${state.tenant}/${state.app_id}/auth/login`;
  let pageAdminConsoleUrl = `/${state.tenant}/${state.app_id}/admin_console/domains`;

  const afterCheckLogin = async (user) => {
    // Check if page active is login page
    const path = window.location.pathname;
    const params = new URLSearchParams(window.location.search);

    const isLoginPage = path.includes(pageLoginUrl);
    const isAdminPage = path.includes(pageAdminConsoleUrl);

    const redirectTo = params.get("redirectTo") || '';
    const isRedirectToAdmin = redirectTo.includes(pageAdminConsoleUrl);

    let pageToRedirect;
    
    if (user) {
      const { disable_user, is_apps_admin, user_email, user_info } = user;
      const { language } = user_info;
      const userIsAdmin = is_apps_admin;

      // Set language
      if (language && LANGUAGE_SUPPORTED.includes(language)) {
        i18n.changeLanguage(language);
      }

      if (isLoginPage) {
        // Redirect to dashboard if not on login page
        if (userIsAdmin) {
          pageToRedirect = redirectTo || pageAdminConsoleUrl;
        } else {
          pageToRedirect = (!isRedirectToAdmin && redirectTo) ? redirectTo : "/";
        }
      } else {
        if (!userIsAdmin && isAdminPage) {
          pageToRedirect = "/";
        }
      }
    } else {
      if (!isLoginPage) {
        pageToRedirect = `${pageLoginUrl}?redirectTo=${encodeURIComponent(path)}`;
      }
    }

    // Only log pageToRedirect if it has a value
    if (pageToRedirect) {
      navigate(pageToRedirect, { replace: true });
    }

    dispatch({
      type: INITIALIZE,
      payload: { 
        isAuthenticated: !!user,
        user
      },
    });
    dispatch({
      type: IS_CHECKING,
      payload: { isChecking: false },
    });
  };

  const loadProfile = async () => {
    // Dispatch checking state
    dispatch({ type: IS_CHECKING, payload: { isChecking: true } });
    dispatch({ type: IS_ERROR, payload: { isError: false, errorMessage: '' } });

    let user;
    try {
      user = await getMe(state.tenant, state.app_id);
    } catch (error) {
      dispatch({
        type: IS_ERROR,
        payload: {
          isError: true,
          errorMessage: error.message,
        },
      });
    }

    afterCheckLogin(user);
  };

  const loginWithGoogle = async () => {
    try {
      // Open popup for Google login
      await openPopupLoginWithGoogle(state.tenant, state.app_id);

      // After the popup closes, reload the profile
      await loadProfile();

      return true;
    } catch (error) {
      console.error('Login with Google failed:', error);
      return false;
    }
  };

  const signOut = async () => {
    try {
      dispatch({ type: IS_CHECKING, payload: { isChecking: true } });

      // Call API to sign out
      await logout(state.tenant, state.app_id); // Assuming this is the sign-out function

      // Dispatch sign-out action
      dispatch({ type: SIGN_OUT });

      // Reset user state
      navigate(pageLoginUrl); // Redirect to login page
    } catch (error) {
      throw 'TXT_SIGN_OUT_ERROR';
    }
  };  const setTenantAppId = (tenant, app_id) => {
    dispatch({ type: SET_TENANT_APP_ID, payload: { tenant, app_id } });
  };

  useEffect(() => {
    if (state.tenant && state.app_id) {
      loadProfile();
    }
  }, [state.tenant, state.app_id]);

  useEffect(() => {
    // Check if the user is authenticated
    if (!state.user && !state.isChecking) {
      // If not authenticated, redirect to login page
      navigate(pageLoginUrl);
    } else {
      const isPageLogin = window.location.pathname.includes(pageLoginUrl);
      if (state.isInitialized && state.isAuthenticated && isPageLogin) {
        navigate(pageAdminConsoleUrl);
      }
    }
  }, [state.isInitialized, state.isAuthenticated, navigate, pageLoginUrl, pageAdminConsoleUrl]);

  return (
    <AuthContext.Provider
      value={{
        ...state,
        method: "jwt",

        user: state.user,
        userInfo: state.userInfo,

        isAuthenticated: state.isAuthenticated,
        isInitialized: state.isInitialized,

        isChecking: state.isChecking,
        isError: state.isError,

        // Actions
        setTenantAppId,
        signOut,
        loginWithGoogle,
        loadProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export default AuthProvider;
