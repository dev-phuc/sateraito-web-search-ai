import React, { useContext, useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { Alert, Button, Dropdown, Offcanvas } from "react-bootstrap";

import { Sliders, BookOpen } from "react-feather";
import ColorPicker from "@/desktop/components/ColorPicker";

import NotyfContext from "@/contexts/NotyfContext";

// import useOuterClick from "@/hooks/useOuterClick";
import useTheme from "@/hooks/useTheme";
import useSidebar from "@/hooks/useSidebar";
import useLayout from "@/hooks/useLayout";

// import { setUserConfigRequest } from "@/utils/request";

import {
  SIDEBAR_POSITION,
  SIDEBAR_BEHAVIOR,
  LAYOUT,
  THEME,
  NOTIFY_CONFIG,
} from "@/constants";

const themeOptions = [
  {
    name: "Default",
    value: THEME.DEFAULT,
  },
  {
    name: "Colored",
    value: THEME.COLORED,
  },
  {
    name: "Dark",
    value: THEME.DARK,
  },
  {
    name: "Light",
    value: THEME.LIGHT,
  },
];

const sidebarPositionOptions = [
  {
    name: "Left",
    value: SIDEBAR_POSITION.LEFT,
  },
  {
    name: "Right",
    value: SIDEBAR_POSITION.RIGHT,
  },
];

const sidebarBehaviorOptions = [
  {
    name: "Sticky",
    value: SIDEBAR_BEHAVIOR.STICKY,
  },
  {
    name: "Fixed",
    value: SIDEBAR_BEHAVIOR.FIXED,
  },
  {
    name: "Compact",
    value: SIDEBAR_BEHAVIOR.COMPACT,
  },
];

const layoutOptions = [
  {
    name: "Fluid",
    value: LAYOUT.FLUID,
  },
  {
    name: "Boxed",
    value: LAYOUT.BOXED,
  },
  {
    name: "Material",
    value: LAYOUT.MATERIAL,
  },
];

function useQuery() {
  return new URLSearchParams(useLocation().search);
}

const OffCanvasSettingTheme = () => {
  const { t } = useTranslation();
  const notyf = useContext(NotyfContext);

  const query = useQuery();
  const [isOpen, setIsOpen] = useState(false);

  const { theme, setTheme, skinColor, setSkinColor } = useTheme();
  const { position, setPosition, behavior, setBehavior } = useSidebar();
  const { layout, setLayout } = useLayout();
  const [isSubmit, setIsSubmit] = useState(false);

  // const innerRef = useOuterClick(() => {
  //   setIsOpen(false);
  // });

  // const setSettingByQueryParam = (name, set) => {
  //   const value = query.get(name);
  //   if (value) {
  //     set(value);
  //   }
  // };

  // // Read from query parameter (e.g. ?theme=dark)
  // // only for demo purposes
  // useEffect(() => {
  //   setSettingByQueryParam("theme", setTheme);
  //   setSettingByQueryParam("sidebarPosition", setPosition);
  //   setSettingByQueryParam("sidebarBehavior", setBehavior);
  //   setSettingByQueryParam("layout", setLayout);
  //   // eslint-disable-next-line react-hooks/exhaustive-deps
  // }, []);

  useEffect(() => {
    if (isSubmit) {
      // console.log("isSubmit=", isSubmit);
      hanldeSave();
    }
  }, [isSubmit]);

  const hanldeChange = async () => {
    setIsSubmit(true);
  };
  const hanldeSave = async () => {
    console.log(
      "hanldeSave SETTING THEME:",
      theme,
      skinColor,
      layout,
      position,
      behavior
    );
    const theme_config = { theme, skinColor, layout, position, behavior };
    await setUserConfigRequest({
      theme_config: JSON.stringify(theme_config),
    });
    notyf.open({
      type: NOTIFY_CONFIG.TYPE.SUCCESS,
      message: t("SUCCESS_SAVE_USER_CONFIG"),
      duration: NOTIFY_CONFIG.DURATION,
      ripple: NOTIFY_CONFIG.RIPPLE,
      dismissible: NOTIFY_CONFIG.DISMISSIBLE,
      position: {
        x: NOTIFY_CONFIG.POSITION.LEFT,
        y: NOTIFY_CONFIG.POSITION.BOTTOM,
      },
    });

    setIsSubmit(false);
  };

  return (
    <React.Fragment>

      <div className="settings-toggle">
        <div
          className="settings-toggle-option settings-toggle-option-text js-settings-toggle"
          title="Theme Builder"
          onClick={() => setIsOpen(true)}
        >
          <Sliders className="feather align-middle" /> {t("LAYOUT_BUILDER_LABEL")}
        </div>
      </div>

      <Offcanvas
        show={isOpen}
        onHide={() => {
          setIsOpen(false);
        }}
        placement="end"
        className="setting-theme-off-canvas"
      >
        <Offcanvas.Header closeButton>
          <Offcanvas.Title>{t("LAYOUT_BUILDER_LABEL")}</Offcanvas.Title>
        </Offcanvas.Header>
        <Offcanvas.Body>
          <div className="settings-body">
            <Alert variant="primary">
              <div className="alert-message"> {t("LAYOUT_BUILDER_DES")}</div>
            </Alert>

            <div className="mb-3">
              <span className="d-block font-size-lg fw-bold">
                {" "}
                {t("BGCOLOR_SCHEME_LABEL")}
              </span>
              {/*<span className="d-block text-muted mb-2">*/}
              {/*  The perfect color mode for your app.*/}
              {/*</span>*/}
              <div className="row g-0 text-center mx-n1 mb-2">
                {themeOptions.map(({ name, value }) => (
                  <div className="col-6" key={value}>
                    <label className="mx-1 d-block mb-1">
                      <input
                        className="settings-scheme-label"
                        type="radio"
                        name="theme"
                        value={value}
                        checked={theme === value}
                        onChange={() => {
                          setTheme(value);
                          hanldeChange();
                        }}
                      />
                      <div className="settings-scheme">
                        <div
                          className={`settings-scheme-theme settings-scheme-theme-${value}`}
                        ></div>
                      </div>
                    </label>
                    {name}
                  </div>
                ))}
              </div>
            </div>
            <hr />
            <div className="mb-3">
              <span className="d-block font-size-lg fw-bold">
                {t("COLOR_SCHEME_LABEL")}
              </span>
              {/*<span className="d-block text-muted mb-2">Change color skin</span>*/}
              <div>
                <ColorPicker
                  onChange={() => {
                    hanldeChange();
                  }}
                ></ColorPicker>
              </div>
            </div>
            <div className="mb-3">
              <span className="d-block font-size-lg fw-bold">
                {t("MENU_POSITION_LABEL")}
              </span>
              {/*<span className="d-block text-muted mb-2">*/}
              {/*  Toggle the position of the sidebar.*/}
              {/*</span>*/}
              <div>
                {sidebarPositionOptions.map(({ name, value }) => (
                  <label className="me-1" key={value}>
                    <input
                      className="settings-button-label"
                      type="radio"
                      name="sidebarPosition"
                      value={value}
                      checked={position === value}
                      onChange={() => {
                        setPosition(value);
                        hanldeChange();
                      }}
                    />
                    <div className="settings-button">{name}</div>
                  </label>
                ))}
              </div>
            </div>
            <hr />
            <div className="mb-3">
              <span className="d-block font-size-lg fw-bold">
                {t("MENU_BEHAVIOR_LABEL")}
              </span>
              {/*<span className="d-block text-muted mb-2">*/}
              {/*  Change the behavior of the sidebar.*/}
              {/*</span>*/}
              <div>
                {sidebarBehaviorOptions.map(({ name, value }) => (
                  <label className="me-1" key={value}>
                    <input
                      className="settings-button-label"
                      type="radio"
                      name="sidebarBehavior"
                      value={value}
                      checked={behavior === value}
                      onChange={() => {
                        setBehavior(value);
                        hanldeChange();
                      }}
                    />
                    <div className={"settings-button " + value}>{name}</div>
                  </label>
                ))}
              </div>
            </div>
            <hr />
            <div className="mb-3">
              <span className="d-block font-size-lg fw-bold">
                {t("LAYOUT_LABEL")}
              </span>
              {/*<span className="d-block text-muted mb-2">*/}
              {/*  Toggle container layout system.*/}
              {/*</span>*/}
              <div>
                {layoutOptions.map(({ name, value }) => (
                  <label className="me-1" key={value}>
                    <input
                      className="settings-button-label"
                      type="radio"
                      name="layout"
                      value={value}
                      checked={layout === value}
                      onChange={() => {
                        setLayout(value);
                        hanldeChange();
                      }}
                    />
                    <div className={"settings-button " + value}>{name}</div>
                  </label>
                ))}
              </div>
            </div>
          </div>
        </Offcanvas.Body>
      </Offcanvas>
    </React.Fragment>
  );
};

export default OffCanvasSettingTheme;
