import { useRef, useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

// Library UI imports
import { Formik } from 'formik';
import { Button, Card, Form } from 'react-bootstrap';

// Hook components
import useTheme from '@/hooks/useTheme'

// Zustand
import useStoreBoxSearchConfig from '@/store/box_search_config';

// Constants
import { BOX_SEARCH_DESIGN_DEFAULT, BOX_SEARCH_TO_HTML_TEMPLATE, SERVER_URL } from '@/constants';

import logoApp from '@/assets/img/sateraito_icon.png';
import logoAppFull from '@/assets/img/logo_rgb.png';

const BoxSearchConfigPreviewPanel = ({ tenant, app_id }) => {
  // Default hooks
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { showNotice } = useTheme();

  const buttonSearchBoxRef = useRef(null);

  // Zustand stores
  const { boxSearchConfigPreview } = useStoreBoxSearchConfig();

  // Use preview data or default values
  const config = boxSearchConfigPreview || BOX_SEARCH_DESIGN_DEFAULT;

  const resultSearchDemo = [
    { title: "Example Result 1", url: "https://example.com/1", favicon: "https://www.google.com/s2/favicons?domain=example.com", description: "This is a description for example result 1 showing how the result will look like in the search results." },
    { title: "Example Result 2", url: "https://example.com/2", favicon: "https://www.google.com/s2/favicons?domain=example.com", description: "This is a description for example result 2 showing how the result will look like in the search results." },
    { title: "Example Result 3", url: "https://example.com/3", favicon: "https://www.google.com/s2/favicons?domain=example.com", description: "This is a description for example result 3 showing how the result will look like in the search results." },
    { title: "Example Result 4", url: "https://example.com/4", favicon: "https://www.google.com/s2/favicons?domain=example.com", description: "This is a description for example result 4 showing how the result will look like in the search results." },
    { title: "Example Result 5", url: "https://example.com/5", favicon: "https://www.google.com/s2/favicons?domain=example.com", description: "This is a description for example result 5 showing how the result will look like in the search results." },
    { title: "Example Result 6", url: "https://example.com/6", favicon: "https://www.google.com/s2/favicons?domain=example.com", description: "This is a description for example result 6 showing how the result will look like in the search results." },
    { title: "Example Result 7", url: "https://example.com/7", favicon: "https://www.google.com/s2/favicons?domain=example.com", description: "This is a description for example result 7 showing how the result will look like in the search results." },
    { title: "Example Result 8", url: "https://example.com/8", favicon: "https://www.google.com/s2/favicons?domain=example.com", description: "This is a description for example result 8 showing how the result will look like in the search results." },
    { title: "Example Result 9", url: "https://example.com/9", favicon: "https://www.google.com/s2/favicons?domain=example.com", description: "This is a description for example result 9 showing how the result will look like in the search results." },
    { title: "Example Result 10", url: "https://example.com/10", favicon: "https://www.google.com/s2/favicons?domain=example.com", description: "This is a description for example result 10 showing how the result will look like in the search results." },
  ];
  const summaryResultDemo = `Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.`;

  // Use state
  const [summaryResult, setSummaryResult] = useState('');
  const [resultTemp, setResultTemp] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const [isShowBackground, setIsShowBackground] = useState(true);
  const [isShowHtml, setIsShowHtml] = useState(false);
  const [isShowBox, setIsShowBox] = useState(false);

  // Render search icon based on config
  const renderSearchIcon = () => {
    const { search_button } = config;

    // Check if is mdi icon
    if (search_button.icon && search_button.icon.startsWith('mdi-')) {
      const iconClass = search_button.icon.replace('mdi-', 'mdi mdi-');
      return <span className={`icon-open ${iconClass}`} style={{ fontSize: '20px' }}></span>;
    }
    // Check if url icon
    if (search_button.icon && (search_button.icon.startsWith('http://') || search_button.icon.startsWith('https://'))) {
      return <img className='icon-open' src={`${search_button.icon}`} alt="Search" style={{ width: '20px', height: '20px' }} />;
    }
    // Check if svg icon
    if (search_button.icon && search_button.icon.startsWith('<svg')) {
      return <span className="icon-open" dangerouslySetInnerHTML={{ __html: search_button.icon }} />;
    }

    return <i className="icon-open mdi mdi-magnify" style={{ fontSize: '20px' }}></i>;
  };

  // Handler
  const onClickButtonSearchBox = () => {
    setIsShowBox(!isShowBox);
  };

  const handlerOnSubmitSearch = (values) => {
    const { query } = values;

    setIsLoading(true);
    setIsSearching(true);

    setTimeout(() => {
      setSummaryResult(summaryResultDemo);
      setResultTemp(resultSearchDemo);

      setIsLoading(false);
    }, 3000);
  }

  // set root color style for preview
  useEffect(() => {
    const { search_box, search_button, theme } = config;

    // search_box
    document.documentElement.style.setProperty('--search-box-bg-color', search_box.options.background_color);
    document.documentElement.style.setProperty('--search-box-border-radius', `${search_box.options.border_radius}px`);
    document.documentElement.style.setProperty('--search-box-border-size', search_box.options.shadow ? `0px` : '1px');
    document.documentElement.style.setProperty('--search-box-padding', `${search_box.options.padding}px`);
    document.documentElement.style.setProperty('--search-box-box-shadow', search_box.options.shadow ? '0 2px 8px rgba(0,0,0,0.15)' : 'none');
    document.documentElement.style.setProperty('--search-box-font-size', `${search_box.options['font-size'] || 16}px`);

    // theme
    document.documentElement.style.setProperty('--theme-color-text-box-search', theme.color);
    document.documentElement.style.setProperty('--theme-color-background-box-search', theme.background_color);
    document.documentElement.style.setProperty('--theme-font-family-box-search', theme.font);

    // search_button
    document.documentElement.style.setProperty('--search-button-color-text', search_button.color);
    document.documentElement.style.setProperty('--search-button-bg-color', search_button.background_color);
    document.documentElement.style.setProperty('--search-button-border-radius', `${search_button.border_radius}px`);

  }, [config]);

  // Return the component
  return (
    <Card className="shadow-sm h-100">
      <Card.Header className="bg-light">
        <div className="d-flex justify-content-between align-items-center">
          {/* Right */}
          <div>
            {!isShowHtml ?
              <>
                <h5 className="mb-0 text-primary"><i className="fas fa-eye me-2"></i>{t('LABEL_PREVIEW')}</h5>
                <small className="text-muted">{t('TXT_PREVIEW_DESC')}</small>
              </>
              :
              <>
                <h5 className="mb-0 text-primary"><i className="fas fa-code me-2"></i>{t('LABEL_SHOW_HTML')}</h5>
                <small className="text-muted">{t('TXT_SHOW_HTML_DESC')}</small>
              </>
            }
          </div>

          {/* Left */}
          <div className="d-flex align-items-center gap-3">
            {!isShowHtml && (
              <>
                <Form.Switch
                  id="switch-show-box-search"
                  label={t('LABEL_SHOW_BOX_SEARCH')}
                  checked={isShowBox}
                  onChange={() => setIsShowBox(!isShowBox)}
                />
                <Form.Switch
                  id="switch-show-background"
                  label={t('LABEL_SHOW_BACKGROUND')}
                  checked={isShowBackground}
                  onChange={() => setIsShowBackground(!isShowBackground)}
                />
              </>
            )}
            <Form.Switch
              id="switch-show-html"
              label={t('LABEL_SHOW_HTML')}
              checked={isShowHtml}
              onChange={() => setIsShowHtml(!isShowHtml)}
            />
          </div>
        </div>
      </Card.Header>
      <Card.Body className="p-4">
        {!isShowHtml ?
          <div className={`preview-container ${config.search_box.type} ${isShowBox ? 'mark-show' : ''} ${isShowBackground ? 'show-background' : 'hide-background'}`}>

            {/* Button right */}
            <div className='d-flex justify-content-end'>
              <button className={`button-search-box ${isShowBox ? 'show-icon-close' : ''}`} type="button" onClick={onClickButtonSearchBox} ref={buttonSearchBoxRef}>
                {renderSearchIcon()}
                <span className="icon-close mdi mdi-close"></span>
              </button>
            </div>

            <div className={`wrap-panel-box-search ${config.search_box.type} ${isShowBox ? 'show' : 'hide'}`}>

              <div className={`panel-box-search ${config.search_box.type} ${isSearching ? 'has-result' : ''}`}>
                <div className={`wrap-header`}>
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
                          <input type="text" name="query" className='input-search-box' placeholder={t('PLACEHOLDER_SEARCH')} value={values.query} onChange={handleChange} />
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
                    {summaryResult}
                  </div>
                  {resultTemp.map((item, index) => (
                    <div key={index} className="result-search-item">
                      <div className="result-search-item-header">
                        {item.favicon && <img src={item.favicon} alt="Favicon" className="result-search-favicon" />}
                        <a href={item.url} target="_blank" rel="noopener noreferrer" className="result-search-title">{item.title}</a>
                      </div>
                      <div className="result-search-item-description">
                        {item.description}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

            </div>

          </div>
          :
          <Card>
            <Card.Body>
              <pre>
                <code>
                  {BOX_SEARCH_TO_HTML_TEMPLATE.replaceAll('SERVER_URL', SERVER_URL).replaceAll('TENANT', tenant).replaceAll('APP_ID', app_id)}
                </code>
              </pre>

              {/* Button copy code to clipboard */}
              <Button onClick={() => {
                navigator.clipboard.writeText(BOX_SEARCH_TO_HTML_TEMPLATE.replaceAll('SERVER_URL', SERVER_URL).replaceAll('TENANT', tenant).replaceAll('APP_ID', app_id));
                showNotice('success', t('NOTICE_COPIED_TO_CLIPBOARD'));
              }} className="btn btn-sm btn-primary">
                <i className="mdi mdi-content-copy me-2"></i>{t('BUTTON_COPY_CODE')}
              </Button>

            </Card.Body>
          </Card>
        }
      </Card.Body>

    </Card>
  );
};

export default BoxSearchConfigPreviewPanel;