// Framework import
import React from "react";
import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { useTranslation } from "react-i18next";

import { DotLottieReact } from '@lottiefiles/dotlottie-react';

// Redux components

// Hook components

// Context components

// Library imports
// Library IU imports
import { Button } from "react-bootstrap";

// Components

// Define the component
const Page404 = () => {
  const { t } = useTranslation();

  return <>
    <Helmet title="404 Error" />
    <div className="page-404">
      <div className="page-404-container">
        <DotLottieReact
          src="https://lottie.host/65f51614-779c-4abb-8b15-de71038f64c5/oAjpf8ZHGP.lottie"
          loop
          autoplay
        />
        <h1 className="page-404-title">{t("TITLE_PAGE_404")}</h1>
        <p className="page-404-description">
          {t("DESC_PAGE_404")}
        </p>
        <div className="page-404-actions">
          <Link to="/">
            <Button variant="primary" size="lg" className="page-404-btn">
              {t("BTN_GO_HOME")}
            </Button>
          </Link>
          <Button variant="outline-primary" size="lg" onClick={() => window.history.back()} className="page-404-btn">
            {t("BTN_GO_BACK")}
          </Button>
        </div>
      </div>
    </div>
  </>
};

export default Page404;
