import { useEffect, useReducer } from "react";

import { requestGetBoards } from "@/utils/request";

import UserSettingContext from "@/contexts/UserSettingContext";

const INITIALIZE = "INITIALIZE";
const SET_GROUPS = "SET_GROUPS";
const SET_LABELS = "SET_LABELS";
const SET_SUGGESTS = "SET_SUGGESTS";
const SET_MEMOS = "SET_MEMOS";
const SET_PINS = "SET_MEMOS";
const initialState = {
  isInitialized: false,
  groups: {},
  labels: {},
  suggests: {},
  memos: {},
  pins: {},
};

const UserSettingReducer = (state, action) => {
  switch (action.type) {
    case INITIALIZE:
      return {
        isInitialized: true,
      };

    case SET_GROUPS:
      return {
        ...state,
        groups: action.payload.groups,
      };

    case SET_LABELS:
      return {
        ...state,
        labels: action.payload.labels,
      };

    case SET_SUGGESTS:
      return {
        ...state,
        suggests: action.payload.suggests,
      };

    case SET_MEMOS:
      return {
        ...state,
        memos: action.payload.memos,
      };

    default:
      return state;
  }
};

function UserSettingProvider({ children }) {
  const [state, dispatch] = useReducer(UserSettingReducer, initialState);

  useEffect(() => {
    const initialize = async () => {
      if (state.isInitialized) return;
      console.log("UserSettingProvider initialize");
      dispatch({
        type: INITIALIZE,
        payload: {},
      });
    };

    initialize();
  }, []);

  const setGroups = async (groups) => {
    dispatch({
      type: SET_GROUPS,
    });
  };

  return (
    <UserSettingContext.Provider
      value={{
        ...state,
        dispatch,
        setGroups,
      }}
    >
      {children}
    </UserSettingContext.Provider>
  );
}

export default UserSettingProvider;
