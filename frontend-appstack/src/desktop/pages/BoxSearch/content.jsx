// Framework import
import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Helmet } from "react-helmet-async";
import { useNavigate, useParams } from 'react-router-dom';

// Hook components
import useTheme from "@/hooks/useTheme";
import useBoxSearch from "@/hooks/useClientBoxSearch";

// Context components

// Library imports

// Library IU imports

// Zustand

// Firebase

// Constant value

// Components
import './index.scss';
import BoxSearchHeader from './header';
import BoxSearchResult from './result';

// Define the component
const BoxSearchPage = () => {
  // Use default
  const { t } = useTranslation();
  const { tenant, app_id } = useParams();
  const { showNotice } = useTheme();

  // Zustand stores

  // Use hooks state
  const { box_search_config, isSearching } = useBoxSearch();

  // state

  const { search_box } = box_search_config || {};

  if (!search_box) {
    return <></>;
  }
  
  // Return component
  return (
    <>
      <div className={`panel-box-search h-100 ${search_box.type} ${isSearching ? 'has-result' : ''}`}>
        <BoxSearchHeader />
        <BoxSearchResult />
      </div>
    </>
  );
};

export default BoxSearchPage;
