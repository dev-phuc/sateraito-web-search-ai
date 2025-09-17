import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

// UI
import { Button } from "react-bootstrap";

// Use Context
import useTheme from "@/hooks/useTheme";
import useSidebar from "@/hooks/useSidebar";
import useLayout from "@/hooks/useLayout";
import useConfig from "@/hooks/useUserConfig";

// Components
import Settings from "@/desktop/components/Settings";
import LanguageConfig from "@/desktop/pages/Setting/OtherSetting/LanguageConfig";

const OtherSetting = () => {
  const { t, i18n } = useTranslation();
  const { tenant, app_id } = useParams();

  // Hooks
  const { theme, skinColor, showNotice } = useTheme();
  const { position, behavior } = useSidebar();
  const { layout } = useLayout();
  const { saveUserConfig } = useConfig();

  // State
  const [isUpdating, setIsUpdating] = useState(false);
  const [configCurrent, setConfigCurrent] = useState(null);
  const [configNew, setConfigNew] = useState(null);

  const handlerSaveSettings = async () => {
    setIsUpdating(true);

    const payload = {
      language: configNew.language,
      config: {
        theme: configNew.theme,
        sidebar_position: configNew.sidebar_position,
        sidebar_behavior: configNew.sidebar_behavior,
        theme_layout: configNew.theme_layout,
        theme_color: configNew.theme_color,
      }
    };

    const { success, message } = await saveUserConfig(tenant, app_id, payload);
    if (success) {
      setConfigCurrent({ ...configNew });
      showNotice('success', t('MSG_UPDATE_USER_CONFIG_SUCCESS'));
    } else {
      showNotice('error', t('MSG_UPDATE_USER_CONFIG_FAILED') + (message ? `: ${message}` : ''));
    }

    setIsUpdating(false);
  };

  const isDisabledSubmit = () => {
    if (!configCurrent || !configNew || isUpdating) {
      return true;
    }
    return JSON.stringify(configCurrent) === JSON.stringify(configNew);
  };

  useEffect(() => {
    const config = {
      language: i18n.language,
      theme: theme,
      sidebar_position: position,
      sidebar_behavior: behavior,
      theme_layout: layout,
      theme_color: skinColor,
    };

    setConfigCurrent(config);
    setConfigNew({ ...config });
  }, []);

  return (
    <>
      <div className="setting-row lg-setting">
        <div className="setting-title">
          <i className="mdi mdi-translate ico"></i>
          {t("LANGUAGE_CONFIG")}
        </div>
        <LanguageConfig onChange={(language) => {
          setConfigNew({ ...configNew, language });
        }}>
        </LanguageConfig>
      </div>

      <div className="setting-row">
        <div className="setting-title">
          <i className="mdi mdi-palette ico"></i>
          <div className="setting-title"> {t("LAYOUT_ANIMATION_LABEL")}</div>
        </div>
        <Settings onChange={(config) => {
          setConfigNew({ ...configNew, ...config, });
        }}></Settings>
      </div>

      <div>
        <div className=" m-2">
          <Button
            type="button"
            className="st-btn-material setting-save"
            disabled={isDisabledSubmit()}
            onClick={handlerSaveSettings}
          >
            {isUpdating ?
              <span className="mdi mdi-spin mdi-loading me-1"></span>
              :
              <span className="mdi mdi-content-save me-1"></span>
            }
            {t("BTN_SAVE")}
          </Button>
        </div>
      </div>
    </>
  );
};

export default OtherSetting;
