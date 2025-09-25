import { useEffect, useReducer, useState } from "react";
import { useParams, useNavigate } from "react-router";

import BoxSearchContext from "@/contexts/BoxSearchContext";

// Firebase
import { signInWithCustomToken } from "firebase/auth";
import { auth } from '@/firebase';

// Requests
import { searchWebActionLLMClient } from "@/request/LLMActions";
import { getFirebaseTokenForClient } from '@/request/clientWebsites';
import { getBoxSearchConfigForClient } from '@/request/boxSearchConfig';

const INITIALIZE = "INITIALIZE";
const SET_FIREBASE_TOKEN = "SET_FIREBASE_TOKEN";
const SET_BOX_SEARCH_CONFIG = "SET_BOX_SEARCH_CONFIG";
const SET_LLM_CONFIGURATION = "SET_LLM_CONFIGURATION";
const SET_CURRENT_CLIENT_WEBSITE = "SET_CURRENT_CLIENT_WEBSITE";
const CLEAR_DATA_SEARCH = "CLEAR_DATA_SEARCH";

const SET_SUMMARY_RESULT = "SET_SUMMARY_RESULT";
const SET_RESOURCE_LIST = "SET_RESOURCE_LIST";
const SET_IS_LOADING = "SET_IS_LOADING";
const SET_IS_SEARCHING = "SET_IS_SEARCHING";
const SET_IS_ERROR = "SET_IS_ERROR";

const initialState = {
  firebase_token: null,
  box_search_config: null,
  llm_configuration: null,

  current_client_website: null,

  query_search: '',

  summary_result: '',
  resource_list: [],

  isInitialized: false,
  isLoading: false,
  isSearching: false,
  isError: false,
  errorMessage: '',
};

const BoxSearchReducer = (state, action) => {
  switch (action.type) {
    case INITIALIZE:
      const { } = action.payload;
      return {
        ...state,
        isInitialized: true,
      };
    case SET_FIREBASE_TOKEN:
      return {
        ...state,
        firebase_token: action.payload,
      };
    case SET_BOX_SEARCH_CONFIG:
      return {
        ...state,
        box_search_config: action.payload,
      };
    case SET_LLM_CONFIGURATION:
      return {
        ...state,
        llm_configuration: action.payload,
      };
    case SET_CURRENT_CLIENT_WEBSITE:
      return {
        ...state,
        current_client_website: action.payload,
      };
    case CLEAR_DATA_SEARCH:
      return {
        ...state,
        query_search: '',
        summary_result: '',
        resource_list: [],
        isSearching: false,
        isLoading: false,
        isError: false,
        errorMessage: '',
      };
    case SET_SUMMARY_RESULT:
      return {
        ...state,
        summary_result: action.payload,
      };
    case SET_RESOURCE_LIST:
      return {
        ...state,
        resource_list: action.payload,
      };
    case SET_IS_LOADING:
      return {
        ...state,
        isLoading: action.payload,
      };
    case SET_IS_SEARCHING:
      return {
        ...state,
        isSearching: action.payload,
      };
    case SET_IS_ERROR:
      return {
        ...state,
        isError: action.payload.isError,
        errorMessage: action.payload.errorMessage,
      };
    default:
      return { ...state };
  }
};

function BoxSearchProvider({ children }) {
  const [state, dispatch] = useReducer(BoxSearchReducer, initialState);

  const { tenant, app_id } = useParams();
  console.log("BoxSearchProvider", tenant, app_id);

  // ================== Message from/to IFrame parent ==================
  const sendToIFrameParent = (message, data) => {
    if (window.parent) {
      window.parent.postMessage({
        type: message,
        data: data,
      }, '*');
    } else {
      console.warn('No parent window found to post message.');
    }
  };
  const sendBoxSearchConfigToIFrameParent = (config) => {
    sendToIFrameParent('box_search_config', config);
  };
  const handleMessageFromIFrameParent = (event) => {
    // For security, you might want to check event.origin here
    if (event.data && event.data.type === 'response_client_web_site') {
      dispatch({ type: SET_CURRENT_CLIENT_WEBSITE, payload: event.data.data });
    }
    if (event.data && event.data.type === 'toggle_panel') {
      if (!event.data.show) {
        // Clear data search
        dispatch({ type: CLEAR_DATA_SEARCH });
      }
    }
  };
  const triggerGetClientWebSiteFromIFrameParent = () => {
    if (window.parent) {
      window.parent.postMessage({
        type: 'request_client_web_site',
      }, '*');
    } else {
      console.warn('No parent window found to post message.');
    }
  };
  // ================================================================

  const processSearchWeb = async (query) => {
    let content = '';
    const { current_client_website } = state;

    dispatch({ type: SET_IS_LOADING, payload: true });
    dispatch({ type: SET_IS_SEARCHING, payload: true });

    searchWebActionLLMClient(tenant, app_id, current_client_website, query, (typeEvent, dataEvent) => {
      dispatch({ type: SET_IS_LOADING, payload: false });

      const { id, event, data } = dataEvent;
      if (!data) return;

      if (typeEvent == 'metadata') {
        const { search_results } = data;
        if (!search_results) return;

        // ReplaceAll "[1]" to link markdown format and target _blank
        let summary = content;
        search_results.forEach((item, index) => {
          const linkMarkdown = `[[${index + 1}]](${item.url})`;
          summary = summary.replaceAll(`[${index + 1}]`, linkMarkdown);
        });

        // Dispatch to state
        dispatch({ type: SET_RESOURCE_LIST, payload: search_results });
        dispatch({ type: SET_SUMMARY_RESULT, payload: summary });

      } else {
        content = data;
        dispatch({ type: SET_SUMMARY_RESULT, payload: data });
      }
    });
  };

  const processUnauthorized = () => {
    // Send to parent to open login page
    sendToIFrameParent('unauthorized', null);
  };

  const loadDataInit = async () => {
    const { current_client_website } = state;
    if (current_client_website) {
      let flowSuccess = true;
      
      // Get Firebase token
      if (flowSuccess && !state.firebase_token) {
        try {
          const { message, token } = await getFirebaseTokenForClient(tenant, app_id, current_client_website);
          if (message === 'success' && token) {
            await signInWithCustomToken(auth, token);
            dispatch({ type: SET_FIREBASE_TOKEN, payload: token });
          } else {
            console.error('Failed to get Firebase token: Invalid response');
          }
        } catch (error) {
          console.error('Failed to get Firebase token:', error);
          flowSuccess = false;
        }
      }

      // Get Box Search Config
      if (flowSuccess && !state.box_search_config) {
        try {
          const { message, config } = await getBoxSearchConfigForClient(tenant, app_id, current_client_website);
          if (message == 'success' && config) {
            // Send config to IFrame parent
            sendBoxSearchConfigToIFrameParent(config);
            dispatch({ type: SET_BOX_SEARCH_CONFIG, payload: config });
          }
        } catch (error) {
          console.error('Failed to get Box Search config:', error);
          flowSuccess = false;
        }
      }

      if (!flowSuccess) {
        const { origin, href } = current_client_website;
        console.error('Unauthorized access to client website:', origin, href);
        processUnauthorized();
      }
    }
  };

  useEffect(() => {
    document.body.style.backgroundColor = 'transparent';

    // Get event click <a> to open new tab
    const handleClickLink = (event) => {
      event.preventDefault();
      
      const target = event.target;
      if (target.tagName === 'A' && target.href) {
        window.open(target.href, '_blank', 'noopener,noreferrer');
      }
    };
    document.addEventListener('click', handleClickLink);
    
    // Set up event listener for messages from parent
    window.addEventListener('message', handleMessageFromIFrameParent);
    // Request client web site from parent
    triggerGetClientWebSiteFromIFrameParent();
    // Clean up event listener on component unmount
    return () => {
      document.removeEventListener('click', handleClickLink);
      window.removeEventListener('message', handleMessageFromIFrameParent);
    };
  }, []);

  useEffect(() => {
    loadDataInit();
  }, [state.current_client_website]);

  useEffect(() => {
    const { box_search_config } = state;
    if (box_search_config) {
      sendBoxSearchConfigToIFrameParent(box_search_config);
      // Apply styles
      const { search_box, search_button, theme } = box_search_config;
      if (search_box) {
        document.documentElement.style.setProperty('--search-box-bg-color', search_box.options.background_color);
        document.documentElement.style.setProperty('--search-box-border-radius', `${search_box.options.border_radius}px`);
        document.documentElement.style.setProperty('--search-box-border-size', search_box.options.shadow ? `0px` : '1px');
        document.documentElement.style.setProperty('--search-box-padding', `${search_box.options.padding}px`);
        document.documentElement.style.setProperty('--search-box-box-shadow', search_box.options.shadow ? '0 2px 8px rgba(0,0,0,0.15)' : 'none');
        document.documentElement.style.setProperty('--search-box-font-size', `${search_box.options['font-size'] || 16}px`);
      }
      if (search_button) {
        document.documentElement.style.setProperty('--search-button-color-text', search_button.color);
        document.documentElement.style.setProperty('--search-button-bg-color', search_button.background_color);
        document.documentElement.style.setProperty('--search-button-border-radius', `${search_button.border_radius}px`);
      }
      if (theme) {
        document.documentElement.style.setProperty('--theme-color-text-box-search', theme.color);
        document.documentElement.style.setProperty('--theme-color-background-box-search', theme.background_color);
        document.documentElement.style.setProperty('--theme-font-family-box-search', theme.font);
        document.documentElement.style.setProperty('--bs-body-font-family', theme.font);
      }
    }
  }, [state.box_search_config]);

  return (
    <BoxSearchContext.Provider
      value={{
        ...state,
        dispatch,

        // Actions
        processSearchWeb,
      }}
    >
      {children}
    </BoxSearchContext.Provider>
  );
}

export default BoxSearchProvider;
