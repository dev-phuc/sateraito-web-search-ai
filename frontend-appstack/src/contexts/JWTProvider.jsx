import { useEffect, useReducer, useState } from "react";
import { useTranslation } from "react-i18next";

import axios from "@/utils/axios";
import { setSession } from "@/utils/jwt";

import AuthContext from "@/contexts/JWTContext";

import LoaderInit from "@/desktop/components/Loader";

import { getMe } from '@/request/auth';

import { KEY_ROLE_CREATOR, LANGUAGE_DEFAULT } from '@/constants';


const INITIALIZE = "INITIALIZE";
const SET_LOADING = "SET_LOADING";
const SIGN_IN = "SIGN_IN";
const SIGN_OUT = "SIGN_OUT";
const SIGN_UP = "SIGN_UP";
const SET_ROLE = "SET_ROLE";

const initialState = {
  isAuthenticated: false,
  isInitialized: false,
  user: null,
  isLoading: true,
};

const JWTReducer = (state, action) => {
  const stateClone = { ...state };

  switch (action.type) {
    case INITIALIZE:
      return {
        isAuthenticated: action.payload.isAuthenticated,
        isInitialized: true,
        user: action.payload.user,
      };
    case SET_LOADING:
      return {
        ...state,
        isLoading: action.payload,
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
        user: null,
      };

    case SIGN_UP:
      return {
        ...state,
        isAuthenticated: true,
        user: action.payload.user,
      };

    case SET_ROLE:
      stateClone.user.role = action.payload.role;
      stateClone.user.is_creator = (action.payload.role == KEY_ROLE_CREATOR);

      return stateClone;

    default:
      return state;
  }
};

function AuthProvider({ children }) {
  const { i18n, t } = useTranslation();
  const [state, dispatch] = useReducer(JWTReducer, initialState);

  // const user = {
  //   "disable_user": null,
  //   "google_apps_domain": null,
  //   "is_apps_admin": null,
  //   "user_email": null,
  //   "user_id": null,
  //   "user_info": {
  //     "family_name": null,
  //     "given_name": null,
  //     "language": null,
  //     "photo_url": null
  //   }
  // };

  const initializeAuth = async (tenant, app_id) => {
    try {
      console.log("AuthProvider initializeAuth");
      dispatch({
        type: SET_LOADING,
        payload: true,
      });

      const user = await getMe(tenant, app_id)
      dispatch({
        type: INITIALIZE,
        payload: {
          isAuthenticated: true,
          user
        },
      });

      // i18n.changeLanguage(user.user_info.language || LANGUAGE_DEFAULT);
      i18n.changeLanguage(LANGUAGE_DEFAULT);

      dispatch({
        type: SET_LOADING,
        payload: false,
      });
    } catch (err) {
      console.error(err);
      dispatch({
        type: INITIALIZE,
        payload: {
          isAuthenticated: false,
          user: null,
        },
      });
    }
  };

  const signIn = async (email, password) => {
    // const response = await axios.post("/api/auth/sign-in", {
    //   email,
    //   password,
    // });
    // const { accessToken, user } = response.data;
    const accessToken = 'woe84tyvwo9e854ytbw9atwemorutvoe8tyvno398tvhsyyyyerp';

    // TEST::
    window.localStorage.setItem(accessToken, JSON.stringify(user));

    setSession(accessToken);
    dispatch({
      type: SIGN_IN,
      payload: {
        user,
      },
    });
  };

  const signOut = async () => {
    setSession(null);
    dispatch({ type: SIGN_OUT });
  };

  const signUp = async (email, password, firstName, lastName) => {
    const response = await axios.post("/api/auth/sign-up", {
      email,
      password,
      firstName,
      lastName,
    });
    const { accessToken, user } = response.data;

    window.localStorage.setItem("accessToken", accessToken);
    dispatch({
      type: SIGN_UP,
      payload: {
        user,
      },
    });
  };

  const sendMailRegister = async (email) => {
  };

  const registerReq = async (formData) => {
    await new Promise((resolve) =>

      // DEMO::
      setTimeout(() => resolve([]), 2000)

    );
  };

  const setRole = async (role) => {
    const { status, data } = await setRoleAuthRequest(role);

    if (status == 'ok') {
      dispatch({
        type: SET_ROLE,
        payload: {
          role,
        },
      });
    }
  }

  const reloadInfoAuth = async () => {
    const { status, data } = await getMe()
    dispatch({
      type: INITIALIZE,
      payload: {
        isAuthenticated: true,
        user: {
          ...user, ...data,
          is_creator: (data.role == KEY_ROLE_CREATOR)
        }
      },
    });
  }

  const isCreator = () => {
    return state.user && state.user.is_creator;
  }

  const isAdmin = () => {
    return state.user && state.user.is_workflow_admin;
  }

  const resetPassword = (email) => console.log(email);

  return (
    <AuthContext.Provider
      value={{
        ...state,
        method: "jwt",

        initializeAuth,

        signIn,
        signOut,
        signUp,
        setRole,
        sendMailRegister,
        registerReq,
        resetPassword,

        isCreator,
        isAdmin,
        reloadInfoAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export default AuthProvider;
