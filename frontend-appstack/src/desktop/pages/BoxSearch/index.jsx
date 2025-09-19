// Framework import
import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Helmet } from "react-helmet-async";
import { useNavigate, useParams } from 'react-router-dom';

// Hook components
import useTheme from "@/hooks/useTheme";

// Context components

// Library imports

// Library IU imports
import { Formik } from "formik";
import { Container, Form } from "react-bootstrap";
import Markdown from 'react-markdown'

// Zustand
import useStoreClientWebsites from '@/store/client_websites';
import useStoreLLMConfiguration from '@/store/llm_configuration';
import useStoreBoxSearchConfig from '@/store/box_search_config';

// Firebase
import { getAuth, signInWithCustomToken } from "firebase/auth";
import firebaseApp, { auth } from '@/firebase';

// Constant value

// Components
import './index.scss';
import logoAppFull from '@/assets/img/logo_rgb.png';
import logoApp from '@/assets/img/sateraito_icon.png';
import SearchResultItem from './SearchResultItem';

// API
import { searchWebActionLLMClient } from "@/request/LLMActions";

// Define the component
const BoxSearchPage = () => {
  // Use default
  const { t } = useTranslation();
  const { tenant, app_id } = useParams();
  const { showNotice } = useTheme();

  // Zustand stores
  const storeClientWebsites = useStoreClientWebsites();
  const { firebaseToken, getFirebaseToken } = storeClientWebsites;

  const storeLLMConfiguration = useStoreLLMConfiguration();
  const { llmConfigurationForClient, getLLMConfigurationForClient } = storeLLMConfiguration;
  const isLoadingLLMConfiguration = storeLLMConfiguration.isLoading;

  const storeBoxSearchConfig = useStoreBoxSearchConfig();
  const { boxSearchConfigForClient, getBoxSearchConfigForClient } = storeBoxSearchConfig;
  const isLoadingBoxSearchConfig = storeBoxSearchConfig.isLoading;

  // Use hooks state

  // state
  const [isSearching, setIsSearching] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [summaryResult, setSummaryResult] = useState('');
  const [searchResult, setSearchResult] = useState([]);

  const [clientWebSite, setClientWebSite] = useState(null);

  const sendBoxSearchConfigToIFrameParent = (config) => {
    if (window.parent) {
      window.parent.postMessage({
        type: 'box_search_config',
        data: config,
      }, '*');
    } else {
      console.warn('No parent window found to post message.');
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
  const handleMessageFromIFrameParent = (event) => {
    // For security, you might want to check event.origin here
    if (event.data && event.data.type === 'response_client_web_site') {
      setClientWebSite(event.data.data);
    }
    if (event.data && event.data.type === 'toggle_panel') {
      if (!event.data.show) {
        // Clear data
        setIsSearching(false);
        setIsLoading(false);
        setSummaryResult('');
        setSearchResult([]);
      }
    }
  };

  const handlerOnSubmitSearch = async (values) => {
    const { query } = values;

    setIsLoading(true);
    setIsSearching(true);

    setSummaryResult('');
    setSearchResult([]);

    await processSearchWebActionLLM(query);
  };

  const processSearchWebActionLLM = async (query) => {
    let content = '';

    searchWebActionLLMClient(tenant, app_id, clientWebSite, query, (typeEvent, dataEvent) => {
      setIsLoading(false);

      const { id, event, data } = dataEvent;
      if (!data) return;

      if (typeEvent == 'metadata') {
        const { search_results } = data;
        setSearchResult(search_results);

        // ReplaceAll "[1]" to link markdown format and target _blank
        let summary = content;
        search_results.forEach((item, index) => {
          const linkMarkdown = `[[${index + 1}]](${item.url})`;
          summary = summary.replaceAll(`[${index + 1}]`, linkMarkdown);
        });
        setSummaryResult(summary);

      } else {
        content = data;
        setSummaryResult(data);
      }
    });
  };

  const handlerLoadData = async () => {
    if (!boxSearchConfigForClient) {
      const { success, message } = await getBoxSearchConfigForClient(tenant, app_id, clientWebSite);
      if (!success) {
        showNotice("danger", t(message));
      }
    }

    if (!llmConfigurationForClient) {
      const { success, message } = await getLLMConfigurationForClient(tenant, app_id, clientWebSite);
      if (!success) {
        showNotice("danger", t(message));
      }
    }

    if (!firebaseToken) {
      const { success, message } = await getFirebaseToken(tenant, app_id, clientWebSite);
      if (!success) {
        showNotice("danger", t(message));
      }
    }
  };

  useEffect(() => {
    if (clientWebSite && tenant && app_id) {
      handlerLoadData();
    }
  }, [clientWebSite]);

  useEffect(() => {
    if (boxSearchConfigForClient) {
      sendBoxSearchConfigToIFrameParent(boxSearchConfigForClient);

      const { search_box, search_button, theme } = boxSearchConfigForClient;
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
  }, [boxSearchConfigForClient]);

  useEffect(() => {
    document.body.style.backgroundColor = 'transparent';

    // Set up event listener for messages from parent
    window.addEventListener('message', handleMessageFromIFrameParent);
    // Request client web site from parent
    triggerGetClientWebSiteFromIFrameParent();
    // Clean up event listener on component unmount
    return () => {
      // window.removeEventListener('message', handleMessageFromIFrameParent);
    };
  }, []);

  useEffect(() => {
    if (firebaseToken) {
      signInWithCustomToken(auth, firebaseToken).then((userCredential) => {
        // Signed in
        const user = userCredential.user;
      }).catch((error) => {
        const errorCode = error.code;
        const errorMessage = error.message;
        console.error('Firebase sign-in error:', errorCode, errorMessage);
      });
    }
  }, [firebaseToken]);

  if (!clientWebSite || !boxSearchConfigForClient || isLoadingLLMConfiguration || isLoadingBoxSearchConfig) {
    return <div className="loading-overlay h-100 w-100 d-flex justify-content-center align-items-center">
      <div className="spinner-border text-primary" role="status">
        <span className="visually-hidden">Loading...</span>
      </div>
    </div>;
  }

  const { search_box, search_button, theme } = boxSearchConfigForClient;

  // Return component
  return (
    <>
      <div className={`panel-box-search h-100 ${search_box.type} ${isSearching ? 'has-result' : ''}`}>

        <div className="wrap-header">
          <span className="logo-app">
            <img src={logoApp} alt="" />
          </span>
          <span className="logo-app-full">
            <img src={logoAppFull} alt="" />
          </span>
          <div className="wrap-input-search">
            <Formik initialValues={{ query: '' }} onSubmit={handlerOnSubmitSearch}>
              {({ handleSubmit, handleChange, values }) => (
                <Form onSubmit={handleSubmit}>
                  <input type="text" name="query" className='input-search-box' style={{ paddingRight: 30 }} placeholder={t('PLACEHOLDER_SEARCH')} value={values.query} onChange={handleChange} />
                </Form>
              )}
            </Formik>
          </div>
        </div>

        {/* Result search */}
        <div className={`result-search-container ${isLoading ? 'is-loading' : ''}`}>
          {isLoading && (
            <div className="loading-overlay">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
            </div>
          )}
          <div className="result-search-summary">
            <Markdown>
              {summaryResult}
            </Markdown>
          </div>
          {searchResult.map((item, index) => (
            <div key={index}>
              <SearchResultItem data={item} />
            </div>
          ))}
        </div>

      </div>
    </>
  );
};

export default BoxSearchPage;
