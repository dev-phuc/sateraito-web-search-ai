import { useEffect, useReducer } from "react";

import UserConfigContext from "@/contexts/UserConfigContext";

import useTheme from "@/hooks/useTheme";
import useSidebar from "@/hooks/useSidebar";
import useLayout from "@/hooks/useLayout";

import {
  SIDEBAR_POSITION,
  SIDEBAR_BEHAVIOR,
  LAYOUT,
  THEME,
} from "@/constants";

const INITIALIZE = "INITIALIZE";
const FETCH_DATA = "FETCH_DATA";
const LOADING = "LOADING";
const ERROR = "ERROR";
const SET_THEME_CONFIG = "SET_THEME_CONFIG";

const getThemeConfigLocalStorage = (key, defaultValue) => {
  const value = window.localStorage.getItem(key);

  if (!value || typeof value == 'undefined') {
    return defaultValue;
  }
  return value.replaceAll('"', '');
}

const initialState = {
  isInitialized: false,
  isLoaded: false,
  isLoading: false,
  isError: false,
  error: {},

  theme_config: {
    theme: getThemeConfigLocalStorage("theme", THEME.DEFAULT),
    skinColor: getThemeConfigLocalStorage("themeSkinColor", THEME.SKIN_COLOR_DEFAULT),
    position: getThemeConfigLocalStorage("sidebarPosition", SIDEBAR_POSITION.LEFT),
    behavior: getThemeConfigLocalStorage("sidebarBehavior", SIDEBAR_BEHAVIOR.STICKY),
    layout: getThemeConfigLocalStorage("layout", LAYOUT.MATERIAL),
  },
};

const UserConfigReducer = (state, action) => {
  switch (action.type) {
    case INITIALIZE:
      return {
        ...state,
        isInitialized: true,
      };

    case FETCH_DATA:
      return {
        ...state,

        theme_config: action.payload.theme_config,

        isError: action.payload.isError,
        error: action.payload.error,
        isLoading: action.payload.isLoading,
        isLoaded: true,
      };

    case LOADING:
      return {
        ...state,
        isLoading: action.payload.isLoading,
        isError: false,
        error: {},
      };

    case ERROR:
      return {
        ...state,
        isError: action.payload.isError,
        error: action.payload.error,
      };

    case SET_THEME_CONFIG:
      return {
        ...state,
        theme_config: action.payload.theme_config,
      };

    default:
      return state;
  }
};

function UserConfigProvider({ children }) {
  const [state, dispatch] = useReducer(UserConfigReducer, initialState);

  const { theme, setTheme, skinColor, setSkinColor } = useTheme();
  const { position, setPosition, behavior, setBehavior } = useSidebar();
  const { layout, setLayout } = useLayout();

  const fetchData = async () => {
    return;
    dispatch({
      type: LOADING,
      payload: {
        isLoading: true,
      },
    });
    const response = await getUserConfigRequest();
    const status = response.status;
    const isError = status === "ng" ? true : false;
    if (isError) {
      dispatch({
        type: ERROR,
        payload: {
          isError: isError,
          error: {
            error_code: response.data.error_code,
            error_message: response.data.error_message,
          },
        },
      });
    } else {
      dispatch({
        type: FETCH_DATA,
        payload: {
          ...response.data,
          isError: isError,
          error: {},
          isLoading: false,
        },
      });
    }
  };

  const setThemeConfig = async (theme_config) => {
    dispatch({
      type: SET_THEME_CONFIG,
      payload: { theme_config },
    });
  };

  useEffect(() => {
    const initialize = async () => {
      if (state.isInitialized) return;
      console.log("UserConfigProvider initialize");
      fetchData();
      dispatch({
        type: INITIALIZE,
        payload: {},
      });
    };

    initialize();
  }, []);

  useEffect(() => {
    if (state.theme_config) {
      // setTheme(state.theme_config.theme);
      // setSkinColor(state.theme_config.skinColor);
      // setPosition(state.theme_config.position);
      // setBehavior(state.theme_config.behavior);
      // setLayout(state.theme_config.layout);
    }
  }, [state.theme_config]);

  return (
    <UserConfigContext.Provider
      value={{
        ...state,
        dispatch,
        fetchData,

        setThemeConfig,
      }}
    >
      {children}
    </UserConfigContext.Provider>
  );
}

export default UserConfigProvider;
