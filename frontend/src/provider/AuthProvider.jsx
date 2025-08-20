import { useRef, useEffect, useReducer } from "react";
import { useNavigate } from "react-router";

import AuthContext from "@/provider/AuthContext";

const INITIALIZE = "INITIALIZE";
const SIGN_OUT = "SIGN_OUT";
const IS_CHECKING = "IS_CHECKING";
const IS_ERROR = "IS_ERROR";

import { ADMIN_ROLE, AVATAR_DEFAULT, USER_ROLE, STAFF_ROLE, MANAGER_ROLE } from "@/constant";
import { getMe, logout, openPopupLoginWithGoogle } from "@/request/auth";

const initialState = {
  isAuthenticated: false,
  isInitialized: false,
  user: null,

  isChecking: false,
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
        isAuthenticated,
        isInitialized: true,
        user,
      };
    case SIGN_OUT:
      return {
        ...state,
        isAuthenticated: false,
        user: null,
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

  const [state, dispatch] = useReducer(reducer, initialState);

  const signOut = async () => {
    try {
      // Call API to sign out
      await logout(); // Assuming this is the sign-out function

      // Dispatch sign-out action
      dispatch({ type: SIGN_OUT });

      // Reset user state
      navigate('/dang-nhap'); // Redirect to login page
    } catch (error) {
      throw 'TXT_SIGN_OUT_ERROR';
    }
  };

  const afterCheckLogin = async (user) => {
    // Check if page active is login page
    const path = window.location.pathname;
    const params = new URLSearchParams(window.location.search);

    const isLoginPage = path.includes("/dang-nhap");
    const isAdminPage = path.includes("/admin");

    const redirectTo = params.get("redirectTo") || '';
    const isRedirectToAdmin = redirectTo.includes("/admin");

    let pageToRedirect;
    
    if (user) {
      const role = user.role || USER_ROLE;

      // Additional user data
      user['isAdmin'] = (role === ADMIN_ROLE);
      user['isManager'] = (role === MANAGER_ROLE);
      user['isStaff'] = (role === STAFF_ROLE);
      user['isUser'] = (role === USER_ROLE);

      if (isLoginPage) {
        // Redirect to dashboard if not on login page
        if (role === ADMIN_ROLE) {
          pageToRedirect = redirectTo || "/overview";
        }
        if (role === MANAGER_ROLE) {
          pageToRedirect = redirectTo || "/overview"; // Managers also go to overview
        }
        if (role === STAFF_ROLE) {
          pageToRedirect = redirectTo || "/store/default"; // Default staff dashboard
        }
        if (role === USER_ROLE) {
          pageToRedirect = (!isRedirectToAdmin && redirectTo) ? redirectTo : "/";
        }
      } else {
        if (role === USER_ROLE && isAdminPage) {
          pageToRedirect = "/";
        }
        if (role === STAFF_ROLE && isAdminPage) {
          pageToRedirect = "/store/default"; // Redirect staff away from admin pages
        }
      }
    } else {
      if (!isLoginPage) {
        pageToRedirect = "/dang-nhap?redirectTo=" + encodeURIComponent(path);
      }
    }

    // Only log pageToRedirect if it has a value
    if (pageToRedirect) {
      console.log('Redirecting to:', pageToRedirect);
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
      user = await getMe();
      if (user) {
        user.isAdmin = (user.role === ADMIN_ROLE);
        user.isManager = (user.role === MANAGER_ROLE);
        user.isStaff = (user.role === STAFF_ROLE);
        user.isUser = (user.role === USER_ROLE);
      }
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
      await openPopupLoginWithGoogle();

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
    if (state.isInitialized && !state.isAuthenticated) {
      // If not authenticated, redirect to login page
      navigate('/dang-nhap');
    } else {
      const isPageLogin = window.location.pathname.includes("/dang-nhap");
      if (state.isInitialized && state.isAuthenticated && isPageLogin) {
        navigate('/overview');
      }
    }
  }, [state.isInitialized, state.isAuthenticated, navigate]);

  const _auth = { ...state.user };

  return (
    <AuthContext.Provider
      value={{
        ...state,
        user: _auth,
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
