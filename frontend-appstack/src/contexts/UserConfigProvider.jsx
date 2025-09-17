import { useEffect, useReducer } from "react";

import UserConfigContext from "@/contexts/UserConfigContext";

const INITIALIZE = "INITIALIZE";
const LOADING = "LOADING";
const ERROR = "ERROR";

import { getUserConfigRequest, updateUserConfigRequest } from "@/request/userConfig";

const initialState = {
  isLoaded: false,
  isLoading: false,
  isError: false,
  error: {},
};

const UserConfigReducer = (state, action) => {
  switch (action.type) {
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

    default:
      return state;
  }
};

function UserConfigProvider({ children }) {
  const [state, dispatch] = useReducer(UserConfigReducer, initialState);

  const getUserConfig = async (tenant, app_id) => {
    try {
      const response = await getUserConfigRequest(tenant, app_id);
      return response;
    } catch (error) {
      throw error;
    }
  };

  const saveUserConfig = async (tenant, app_id, config) => {
    const result = {
      success: false,
      message: "",
    };
    try {
      const response = await updateUserConfigRequest(tenant, app_id, config);
      result.success = true;
      result.message = response.message;
    } catch (error) {
      const { response } = error;
      result.success = false;
      result.message = response?.data?.message || error.message;
    }
    return result;
  };

  return (
    <UserConfigContext.Provider
      value={{
        ...state,
        dispatch,

        getUserConfig,
        saveUserConfig,
      }}
    >
      {children}
    </UserConfigContext.Provider>
  );
}

export default UserConfigProvider;
