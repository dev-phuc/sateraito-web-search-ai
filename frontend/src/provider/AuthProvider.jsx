import { useRef, useEffect, useReducer } from "react";
import { useParams, useNavigate } from "react-router";

import AuthContext from "@/provider/AuthContext";

const INITIALIZE = "INITIALIZE";
const SIGN_OUT = "SIGN_OUT";
const IS_CHECKING = "IS_CHECKING";
const IS_ERROR = "IS_ERROR";

import i18n from "@/locales";
import { LANGUAGE_SUPPORTED } from "@/constant";
import { getMe, logout, openPopupLoginWithGoogle } from "@/request/auth";

const initialState = {
  isAuthenticated: false,
  isInitialized: false,

  user: null,
  userInfo: null,

  isChecking: true,
  isError: false,
  errorMessage: '',
};

const reducer = (state, action) => {
  const { type, payload } = action;

  switch (type) {
    case INITIALIZE:
      const { isAuthenticated, user } = payload;
      return {
        ...state,
        user,
        isAuthenticated,
        isInitialized: true,
        userInfo: user ? user.user_info : null,
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
        isChecking: payload.isChecking,
      };
    case IS_ERROR:
      return {
        ...state,
        isError: payload.isError,
        errorMessage: payload.errorMessage,
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
  const navigate = useNavigate();
  const { tenant, app_id } = useParams();

  let pageLoginUrl = `/${tenant}/${app_id}/login`;
  let pageAdminConsoleUrl = `/${tenant}/${app_id}/admin_console`;
  
  const [state, dispatch] = useReducer(reducer, initialState);

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
        pageToRedirect = `/${pageLoginUrl}?redirectTo=${encodeURIComponent(path)}`;
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
      user = await getMe(tenant, app_id);
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

  const signOut = async (tenant, app_id) => {
    try {
      dispatch({ type: IS_CHECKING, payload: { isChecking: true } });

      // Call API to sign out
      await logout(tenant, app_id); // Assuming this is the sign-out function

      // Dispatch sign-out action
      dispatch({ type: SIGN_OUT });

      // Reset user state
      navigate(pageLoginUrl); // Redirect to login page
    } catch (error) {
      throw 'TXT_SIGN_OUT_ERROR';
    }
  };

  const loginWithGoogle = async () => {
    try {
      // Open popup for Google login
      await openPopupLoginWithGoogle(tenant, app_id);

      // After the popup closes, reload the profile
      await loadProfile();

    } catch (error) {
      console.error('Login with Google failed:', error);
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

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
  }, [state.isInitialized, state.isAuthenticated, navigate]);

  return (
    <AuthContext.Provider
      value={{
        ...state,
        user: state.user,
        userInfo: state.userInfo,

        isAuthenticated: state.isAuthenticated,
        isInitialized: state.isInitialized,

        isChecking: state.isChecking,
        isError: state.isError,

        // Actions
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
