// Framework import
import React, { } from "react";
import { useTranslation } from "react-i18next";

// Hook components

// Context components
import useBoxSearch from "@/hooks/useClientBoxSearch";

// Library imports

// Library IU imports
import { Formik } from "formik";
import { Form } from "react-bootstrap";

// Zustand

// Firebase

// Constant value

// Components
import logoAppFull from '@/assets/img/logo_rgb.png';
import logoApp from '@/assets/img/sateraito_icon.png';

// Define the component
const BoxSearchHeader = ({ }) => {
  // Use default
  const { t } = useTranslation();

  // Hooks context
  const { processSearchWeb } = useBoxSearch();

  // Zustand stores

  // State

  const handlerOnSubmitSearch = async (values) => {
    const { query } = values;
    if (!query || query.trim() === '') {
      return;
    }
    
    processSearchWeb(query);
  };

  // Return component
  return (
    <>
      <div className="wrap-header">
        <span className="logo-app">
          <img src={logoApp} alt="" />
        </span>
        <span className="logo-app-full">
          <img src={logoAppFull} alt="" />
        </span>
        <div className="wrap-input-search">
          <Formik initialValues={{ query: '' }} onSubmit={handlerOnSubmitSearch}>
            {({ handleSubmit, handleChange, values }) => (
              <Form onSubmit={handleSubmit}>
                <input type="text" name="query" className='input-search-box' placeholder={t('PLACEHOLDER_SEARCH')}
                  style={{ paddingRight: 30 }}
                  value={values.query}
                  onChange={handleChange}
                />
              </Form>
            )}
          </Formik>
        </div>
      </div>
    </>
  );
};

export default BoxSearchHeader;
