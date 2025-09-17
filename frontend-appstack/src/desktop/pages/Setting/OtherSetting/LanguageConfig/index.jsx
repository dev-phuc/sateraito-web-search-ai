import React from "react";
import { useTranslation } from "react-i18next";
import { Dropdown } from "react-bootstrap";
import { LANGUAGE_OPTIONS } from "@/constants";

const NavbarLanguages = ({ onChange }) => {
  const { i18n } = useTranslation();

  const selectedLanguage = LANGUAGE_OPTIONS[i18n.language];

  return (
    <Dropdown className="nav-item" align="bottom">

      <Dropdown.Toggle as="a" className="nav-link nav-flag language-setting">
        <img src={selectedLanguage.icon} alt={selectedLanguage.name} />
        <span>{selectedLanguage.name}</span>
      </Dropdown.Toggle>

      <Dropdown.Menu>
        {Object.keys(LANGUAGE_OPTIONS).map((language) => (
          <Dropdown.Item
            key={language}
            onClick={() => {
              i18n.changeLanguage(language);
              onChange(language);
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
    </Dropdown>
  );
};

NavbarLanguages.defaultProps = {
  onChange: (language) => { },
};

export default NavbarLanguages;
