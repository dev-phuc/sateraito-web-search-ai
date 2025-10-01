// Framework import
import React from "react";
import { Helmet } from "react-helmet-async";
import { useTranslation } from "react-i18next";

// Redux components

// Hook components

// Context components

// Library imports
// Library IU imports
import { Container, Row, Spinner } from "react-bootstrap";

import SVGLoading from '@/assets/img/90-ring.svg';

// Define the component
const Loader = () => {
  const { t } = useTranslation();

  return (
    <Container fluid className="vh-50 d-flex loader-component">
      <Helmet>
        <title>{t('TXT_LOADING')} 🚀</title>
      </Helmet>

      <Row className="justify-content-center align-self-center w-100 text-center">
        {/* <Spinner animation="border" /> */}
        <img src={SVGLoading} alt={t('TXT_LOADING')} className="loader-svg" />
        <div className="mt-3">{t('TXT_LOADING')}</div>
      </Row>
    </Container>
  )
};

export default Loader;
