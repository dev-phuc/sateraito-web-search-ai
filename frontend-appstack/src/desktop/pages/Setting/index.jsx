import React from "react";
import { useTranslation } from "react-i18next";
import { Helmet } from "react-helmet-async";

import { Col, Container, Nav, Row, Tab } from "react-bootstrap";

import OtherSetting from "@/desktop/pages/Setting/OtherSetting";

const SettingAdminConsolePage = () => {
  const { t } = useTranslation();
  return (
    <>
      <Helmet title={t("PAGE_TITLE_OTHER_SETTINGS")} />

      <Container fluid className="setting-page">
        <OtherSetting></OtherSetting>
      </Container>
    </>
  );
};

export default SettingAdminConsolePage;
