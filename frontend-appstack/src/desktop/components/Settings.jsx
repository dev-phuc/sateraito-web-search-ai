import React, { useContext, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { Col, Row } from "react-bootstrap";

import ColorPicker from "@/desktop/components/ColorPicker";

import NotyfContext from "@/contexts/NotyfContext";
import useTheme from "@/hooks/useTheme";
import useSidebar from "@/hooks/useSidebar";
import useLayout from "@/hooks/useLayout";

import {
  SIDEBAR_POSITION,
  SIDEBAR_BEHAVIOR,
  LAYOUT,
  THEME,
  NOTIFY_CONFIG,
} from "@/constants";

const Settings = ({ onChange }) => {
  const { t } = useTranslation();
  const notyf = useContext(NotyfContext);

  const [isSubmit, setIsSubmit] = useState(false);

  const { theme, setTheme } = useTheme();
  const { position, setPosition, behavior, setBehavior } = useSidebar();
  const { layout, setLayout } = useLayout();

  const themeOptions = [
    {
      name: t('TXT_THEME_DEFAULT'),
      value: THEME.DEFAULT,
    },
    {
      name: t('TXT_THEME_COLORED'),
      value: THEME.COLORED,
    },
    {
      name: t('TXT_THEME_DARK'),
      value: THEME.DARK,
    },
    {
      name: t('TXT_THEME_LIGHT'),
      value: THEME.LIGHT,
    },
  ];

  const sidebarPositionOptions = [
    {
      name: t('TXT_SIDEBAR_LEFT'),
      value: SIDEBAR_POSITION.LEFT,
    },
    {
      name: t('TXT_SIDEBAR_RIGHT'),
      value: SIDEBAR_POSITION.RIGHT,
    },
  ];

  const sidebarBehaviorOptions = [
    {
      name: t('TXT_SIDEBAR_BEHAVIOR_STICKY'),
      value: SIDEBAR_BEHAVIOR.STICKY,
    },
    {
      name: t('TXT_SIDEBAR_BEHAVIOR_FIXED'),
      value: SIDEBAR_BEHAVIOR.FIXED,
    },
    {
      name: t('TXT_SIDEBAR_BEHAVIOR_COMPACT'),
      value: SIDEBAR_BEHAVIOR.COMPACT,
    },
  ];

  const layoutOptions = [
    {
      name: t('TXT_LAYOUT_FLUID'),
      value: LAYOUT.FLUID,
    },
    {
      name: t('TXT_LAYOUT_BOXED'),
      value: LAYOUT.BOXED,
    },
    {
      name: t('TXT_LAYOUT_MATERIAL'),
      value: LAYOUT.MATERIAL,
    },
  ];

  const handlerChange = async (config) => {
    onChange(config);
  };

  return (
    <>
      <div className="settings-body p-3">
        <Row>

          <div className="mb-4">
            <Col md={12}>
              <span className="d-block font-size-lg fw-bold">
                {t("COLOR_SCHEME_LABEL")}
              </span>
              <div>
                <ColorPicker onChange={(value) => {
                  handlerChange({
                    theme_color: value,
                  });
                }}
                ></ColorPicker>
              </div>
            </Col>
          </div>

          <Col md={2}>
            <span className="d-block font-size-lg fw-bold">
              {" "}
              {t("BG_COLOR_SCHEME_LABEL")}
            </span>
            <div className="row g-0 text-center mx-n1 mb-2">
              {themeOptions.map(({ name, value }) => (
                <div className="col-6" key={value}>
                  <label className="mx-1 d-block mb-1">
                    <input className="settings-scheme-label" type="radio" name="theme"
                      value={value} checked={theme === value} onChange={() => {
                        setTheme(value);
                        handlerChange({
                          theme: value,
                        });
                      }}
                    />
                    <div className="settings-scheme">
                      <div className={`settings-scheme-theme settings-scheme-theme-${value}`}></div>
                    </div>
                  </label>
                  {name}
                </div>
              ))}
            </div>
          </Col>

          <Col md={4}>
            <div className="mb-3">
              <span className="d-block font-size-lg fw-bold">
                {t("MENU_POSITION_LABEL")}
              </span>
              <div>
                {sidebarPositionOptions.map(({ name, value }) => (
                  <label className="me-1" key={value}>
                    <input className="settings-button-label" type="radio" name="sidebarPosition"
                      value={value} checked={position === value} onChange={() => {
                        setPosition(value);
                        handlerChange({
                          sidebar_position: value,
                        });
                      }}
                    />
                    <div className="settings-button">{name}</div>
                  </label>
                ))}
              </div>
            </div>

            <div className="mb-3">
              <span className="d-block font-size-lg fw-bold">
                {t("MENU_BEHAVIOR_LABEL")}
              </span>
              <div>
                {sidebarBehaviorOptions.map(({ name, value }) => (
                  <label className="me-1" key={value}>
                    <input className="settings-button-label" type="radio" name="sidebarBehavior"
                      value={value} checked={behavior === value} onChange={() => {
                        setBehavior(value);
                        handlerChange({
                          sidebar_behavior: value,
                        });
                      }}
                    />
                    <div className={"settings-button " + value}>{name}</div>
                  </label>
                ))}
              </div>
            </div>

            <div className="mb-3">
              <span className="d-block font-size-lg fw-bold">
                {t("LAYOUT_LABEL")}
              </span>
              <div>
                {layoutOptions.map(({ name, value }) => (
                  <label className="me-1" key={value}>
                    <input className="settings-button-label" type="radio" name="layout"
                      value={value} checked={layout === value} onChange={() => {
                        setLayout(value);
                        handlerChange({
                          theme_layout: value,
                        });
                      }}
                    />
                    <div className={"settings-button " + value}>{name}</div>
                  </label>
                ))}
              </div>
            </div>
          </Col>
        </Row>
      </div>
    </>
  );
};

Settings.defaultProps = {
  onChange: (config) => { },
};

export default Settings;
