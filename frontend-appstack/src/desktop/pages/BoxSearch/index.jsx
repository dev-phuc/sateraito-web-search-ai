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
import { Container } from "react-bootstrap";

// Zustand
import useStoreLLMConfiguration from '@/store/llm_configuration';
import useStoreBoxSearchConfig from '@/store/box_search_config';

// Constant value

// Components
import './index.scss';
import logoAppFull from '@/assets/img/logo_rgb.png';
import logoApp from '@/assets/img/sateraito_icon.png';

// Define the component
const BoxSearchPage = () => {
  // Use default
  const { t } = useTranslation();
  const { tenant, app_id } = useParams();

  // Zustand stores
  const storeLLMConfiguration = useStoreLLMConfiguration();
  const { llmConfigurationForClient, getLLMConfigurationForClient } = storeLLMConfiguration;
  const isLoadingLLMConfiguration = storeLLMConfiguration.isLoading;

  const storeBoxSearchConfig = useStoreBoxSearchConfig();
  const { boxSearchConfigForClient, getBoxSearchConfigForClient } = storeBoxSearchConfig;
  const isLoadingBoxSearchConfig = storeBoxSearchConfig.isLoading;

  // Use hooks state

  // state
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
  };

  useEffect(() => {
    if (clientWebSite && tenant && app_id) {
      getLLMConfigurationForClient(tenant, app_id, clientWebSite);
      getBoxSearchConfigForClient(tenant, app_id, clientWebSite);
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

  if (!clientWebSite || !boxSearchConfigForClient || isLoadingLLMConfiguration || isLoadingBoxSearchConfig) {
    return <div>Loading...</div>;
  }

  const { search_box, search_button, theme } = boxSearchConfigForClient;

  // Return component
  return (
    <>
      <div className="h-100">
        <div className={`panel-box-search ${search_box.type}`}>

          <div className="wrap-header">
            <span className="logo-app">
              <img src={logoApp} alt="" />
            </span>
            <span className="logo-app-full">
              <img src={logoAppFull} alt="" />
            </span>
            <div className="wrap-input-search">
              <input type="text" className='input-search-box' placeholder={t('PLACEHOLDER_SEARCH')} />
            </div>
          </div>

        </div>
      </div>
    </>
  );
};

export default BoxSearchPage;
