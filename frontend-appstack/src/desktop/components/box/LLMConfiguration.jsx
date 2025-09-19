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
      <div className="bg-light pb-1">
        <div className="wrap-box">

          <div className="box-header d-flex align-items-center px-2 justify-content-between">
            <div className="box-header-left d-flex align-items-center justify-content-start">
              <span className="mdi mdi-robot-outline mdi-24px me-2"></span>
              <h5 className="mb-0">{t("LABEL_LLM_CONFIGURATION")}</h5>
            </div>
            {/* Menu */}
            <div>
              <Dropdown>
                <Dropdown.Toggle className="btn btn-sm btn-light rounded-circle">
                  <span className="mdi mdi-dots-vertical"></span>
                </Dropdown.Toggle>
                <Dropdown.Menu align="end">
                  <Dropdown.Item onClick={handlerOnClickEdit}>
                    <span className="mdi mdi-pencil-outline me-2"></span>
                    {t("BTN_EDIT")}
                  </Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
            </div>
          </div>

          <div className="box-content box-content px-4">
            {llmConfiguration && (
              <>
                <div>
                  <p className='mb-2'>
                    <strong>{t("LABEL_MODEL_NAME")}:</strong> <span className="ms-2 badge bg-info">{llmConfiguration?.model_name}</span>
                  </p>
                  <p className='mb-2'>
                    <strong>{t("LABEL_RESPONSE_LENGTH_LEVEL")}:</strong>
                    <span className={`ms-2 badge bg-${getBadgeVariant(llmConfiguration?.response_length_level)}`}>
                      {llmConfiguration?.response_length_level ? t(`LABEL_RESPONSE_${llmConfiguration.response_length_level.toUpperCase()}`) : t("TXT_NOT_SET")}
                    </span>
                  </p>
                  {llmConfiguration && llmConfiguration.system_prompt && (
                    <div className='mb-2'>
                      <strong>{t("LABEL_SYSTEM_PROMPT")}:</strong>

                      <div className='bg-white p-2 border rounded'>
                        <Markdown>
                          {llmConfiguration.system_prompt}
                        </Markdown>
                      </div>
                    </div>
                  )}
                </div>
              </>
            )}

            {isLoading && <MakerLoading opacity="10" />}
          </div>

        </div>
      </div>
    </>
  );
};

export default LLMConfigurationBox;