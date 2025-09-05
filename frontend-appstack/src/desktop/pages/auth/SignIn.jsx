// Framework import
import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { useTranslation } from "react-i18next";

// Hook components
import useAuth from "@/hooks/useAuth";
import useTheme from "@/hooks/useTheme";

// Context components

// Library imports
// Library IU imports
import { Button, Form, Container, Row, Col, Card } from "react-bootstrap";

// Components
import LogoApp from "@/assets/img/logo.svg";
import GoogleLogo from "@/assets/img/icons/google-96.svg";
import styles from "./SignIn.module.scss";

// Define the component
const SignInPage = () => {
  // Use default
  const { t } = useTranslation();

  // State
  const [isLoading, setIsLoading] = useState(false);

  // Use hooks state
  const { showNotice } = useTheme();

  const { loginWithGoogle } = useAuth();

  const handleGoogleSignIn = async () => {
    setIsLoading(true);

    // Handle Google sign in logic here
    const isSuccess = await loginWithGoogle();

    setIsLoading(false);

    if (!isSuccess) {
      showNotice('error', t('TXT_LOGIN_FAILED_PLEASE_TRY_AGAIN'));
    }
  };

  return (
    <>
      <Helmet>
        <title>{t('PAGE_TITLE_LOGIN')}</title>
      </Helmet>

      <div className={styles["signin-bg"]}>
        <Container style={{ maxWidth: 400 }}>
          <Card className={styles["signin-card"]}>
            <Card.Body>
              <img src={LogoApp} className={styles["signin-logo"]} alt="Logo" />
              <h2 className={styles["signin-title"]}>{t('TXT_COMPANY_NAME')}</h2>
              <h2 className={styles["signin-title"]}>{t('TXT_APP_NAME')}</h2>
              <div className={styles["signin-desc"]}>{t('TXT_APP_DESCRIPTION')}</div>
              <Button
                disabled={isLoading}
                variant="outline-primary"
                className={"w-100 d-flex align-items-center justify-content-center gap-2 py-2 " + styles["google-btn"]}
                onClick={handleGoogleSignIn}
              >
                <img
                  src={GoogleLogo}
                  alt="Google logo"
                  style={{ width: 28, height: 28 }}
                  className="me-2"
                />
                {t('TXT_LOGIN_WITH_GOOGLE')}
              </Button>
            </Card.Body>
          </Card>
        </Container>
      </div>
    </>
  );
};

export default SignInPage;
