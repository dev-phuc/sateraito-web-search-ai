import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';

// Library UI imports
import Markdown from 'react-markdown';
import { Dropdown } from 'react-bootstrap';

// Hook components

// Zustand
import useStoreLLMConfiguration from '@/store/llm_configuration';

// Constants

// Component
import MakerLoading from '@/desktop/components/MakerLoading';

const LLMConfigurationBox = ({ }) => {
  // Default hooks
  const { tenant, app_id } = useParams();
  const navigate = useNavigate();
  const { t } = useTranslation();

  // Zustand stores
  const { isLoading, llmConfiguration, getLLMConfiguration } = useStoreLLMConfiguration();

  // Use hooks state

  // state

  // Handler
  const handlerLoadData = async () => {
    const { success, message } = await getLLMConfiguration(tenant, app_id);
    if (!success) {
      showNotice("danger", t(message));
    }
  };

  const getBadgeVariant = (status) => {
    switch (status) {
      case 'low':
        return 'info';
      case 'medium':
        return 'warning';
      case 'high':
        return 'danger';
      default:
        return 'light';
    }
  };

  const handlerOnClickEdit = () => {
    navigate(`/${tenant}/${app_id}/admin_console/ai-configuration`);
  }

  // Effects
  useEffect(() => {
    if (!isLoading && !llmConfiguration) {
      handlerLoadData();
    }
  }, []);

  // Return the component
  return (
    <>
      <div className="llm-configuration-box ">
        {/* Modern Card Container */}
        <div className="card ">
          
          {/* Header Section */}
          <div className="card-header border-0 ">
            <div className="d-flex align-items-center justify-content-between flex-wrap">
              {/* Header Left */}
              <div className="d-flex align-items-center mb-2 mb-lg-0">
                {/* <div className="me-3 p-2 rounded-circle" style={{
                  background: 'linear-gradient(45deg, #667eea, #764ba2)',
                  color: 'white', width: '48px', height: '48px', display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}>
                  <i className="mdi mdi-robot-outline" style={{ fontSize: '24px' }}></i>
                </div> */}
                <div>
                  <h4 className="mb-0 fw-bold text-dark">{t("LABEL_LLM_CONFIGURATION")}</h4>
                  {llmConfiguration ? (
                    <div className="d-flex align-items-center gap-2 mt-1">
                      <span className="badge ai-model px-2 py-1 rounded-pill small chip">
                        <i className="mdi mdi-robot "></i>
                        {llmConfiguration.model_name}
                      </span>
                      <span className={`badge bg-${getBadgeVariant(llmConfiguration?.response_length_level)} px-2 py-1 rounded-pill small chip`}>
                        <i className="mdi mdi-gauge "></i>
                        {llmConfiguration?.response_length_level ? t(`LABEL_RESPONSE_${llmConfiguration.response_length_level.toUpperCase()}`) : t("TXT_NOT_SET")}
                      </span>
                    </div>
                  ) : (
                    <small className="text-muted">AI Model Settings & Configuration</small>
                  )}
                </div>
              </div>
              
              {/* Action Menu */}
              <Dropdown>
                <Dropdown.Toggle 
                  className="btn st-btn-material-outline"
                  variant=''
                >
                  <i className="mdi mdi-cog-outline me-1"></i>
                  Actions
                </Dropdown.Toggle>
                <Dropdown.Menu align="end" className="shadow border-0">
                  <Dropdown.Item onClick={handlerOnClickEdit} className="d-flex align-items-center">
                    <i className="mdi mdi-pencil-outline me-2 text-primary"></i>
                    <span>{t("BTN_EDIT")}</span>
                  </Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
            </div>
          </div>

          {/* Content Section */}
          <div className="card-body " >
            {llmConfiguration && (
              <>
                {/* System Prompt Section */}
                {llmConfiguration && llmConfiguration.system_prompt && (
                  <div>
                    <div className="d-flex align-items-center d-none">
                      <i className="mdi mdi-message-text-outline text-success me-2" style={{ fontSize: '20px' }}></i>
                      <h6 className="mb-0 fw-bold text-dark">{t("LABEL_SYSTEM_PROMPT")}</h6>
                    </div>
                    
                    <div className="position-relative">
                      <div 
                        className="p-4 rounded-3 shadow-sm"
                        style={{
                          background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
                          border: '1px solid #dee2e6',
                          maxHeight: '300px',
                          overflowY: 'auto'
                        }}
                      >
                        <div style={{
                          fontFamily: 'SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
                          fontSize: '0.875rem',
                          lineHeight: '1.6',
                          color: '#495057'
                        }}>
                          <Markdown
                            components={{
                              p: ({children}) => <p className="mb-2">{children}</p>,
                              h1: ({children}) => <h5 className="fw-bold text-primary mb-2">{children}</h5>,
                              h2: ({children}) => <h6 className="fw-bold text-secondary mb-2">{children}</h6>,
                              ul: ({children}) => <ul className="ps-3 mb-2">{children}</ul>,
                              ol: ({children}) => <ol className="ps-3 mb-2">{children}</ol>,
                              li: ({children}) => <li className="mb-1">{children}</li>,
                              code: ({children}) => <code className="bg-light px-1 rounded text-danger">{children}</code>
                            }}
                          >
                            {llmConfiguration.system_prompt}
                          </Markdown>
                        </div>
                      </div>
                      
                    </div>
                  </div>
                )}
              </>
            )}

            {/* Loading State */}
            {isLoading && (
              <div className="d-flex flex-column align-items-center justify-content-center py-5">
                <div className="spinner-border text-primary mb-3" role="status">
                  <span className="visually-hidden">Loading...</span>
                </div>
                <p className="text-muted mb-0">Loading configuration...</p>
              </div>
            )}

            {/* Empty State */}
            {!isLoading && !llmConfiguration && (
              <div className="text-center py-5">
                <i className="mdi mdi-robot-dead-outline text-muted mb-3" style={{ fontSize: '4rem' }}></i>
                <h6 className="text-muted mb-2">No Configuration Found</h6>
                <p className="text-muted small">Please set up your LLM configuration to get started.</p>
                <button 
                  className="btn btn-primary btn-sm rounded-pill px-4"
                  onClick={handlerOnClickEdit}
                >
                  <i className="mdi mdi-plus me-1"></i>
                  Setup Configuration
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default LLMConfigurationBox;