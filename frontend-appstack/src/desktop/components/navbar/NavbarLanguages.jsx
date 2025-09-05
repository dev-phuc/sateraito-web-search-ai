import React, { useState } from "react";
import { useTranslation } from "react-i18next";

// Hook components
import useAuth from "@/hooks/useAuth";

// Library imports
// Library IU imports
import { Dropdown, Spinner } from "react-bootstrap";

// Constant
import { KEY_REQUEST_SUCCESS, LANGUAGE_OPTIONS } from "@/constants";

// Requests

const NavbarLanguages = () => {
  const { i18n } = useTranslation();

  const { user } = useAuth();

  const [isLoadingSetLang, setIsLoadingSetLang] = useState(false);

  const selectedLanguage = LANGUAGE_OPTIONS[i18n.language];

  const handlerSetLanguage = async (language) => {
    if (!user) {
      i18n.changeLanguage(language);
      return;
    }
    
    setIsLoadingSetLang(true);
    if (status == KEY_REQUEST_SUCCESS) {
      i18n.changeLanguage(language);
    }
    setIsLoadingSetLang(false);
  }

  return (
    <Dropdown className="me-2 nav-item nav-language" align="end">
      <Dropdown.Toggle as="a" className="nav-link nav-flag">
        <img src={selectedLanguage.icon} alt={selectedLanguage.name} />
      </Dropdown.Toggle>
      <Dropdown.Menu>
        {Object.keys(LANGUAGE_OPTIONS).map((language) => (
          <Dropdown.Item
            key={language}
            onClick={() => {
              handlerSetLanguage(language);
            }}
          >
            <img
              src={LANGUAGE_OPTIONS[language].icon}
              alt={LANGUAGE_OPTIONS[language].name}
              width="20"
              className="align-middle me-1"
            />
            <span className="align-middle">
              {LANGUAGE_OPTIONS[language].name}
            </span>
          </Dropdown.Item>
        ))}
      </Dropdown.Menu>

      {isLoadingSetLang && (
        <Spinner />
      )}
    </Dropdown>
  );
};

export default NavbarLanguages;
