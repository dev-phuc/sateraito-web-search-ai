// Framework import
import React, { } from "react";
import { useTranslation } from "react-i18next";
import { useParams } from 'react-router-dom';

// Hook components
import useTheme from "@/hooks/useTheme";

// Context components
import useBoxSearch from "@/hooks/useClientBoxSearch";

// Library imports

// Library IU imports
import Markdown from 'react-markdown'

// Zustand

// Firebase

// Constant value

// Components
import SearchResultItem from './SearchResultItem';

// API

// Define the component
const BoxSearchResult = ({ }) => {
  // Use default
  const { t } = useTranslation();
  const { tenant, app_id } = useParams();
  const { showNotice } = useTheme();

  // Zustand stores

  // Hooks context
  const { summary_result, resource_list, isLoading } = useBoxSearch();

  // Return component
  return (
    <>
      <div className={`result-search-container ${isLoading ? 'is-loading' : ''}`}>
        {isLoading && (
          <div className="loading-overlay">
            <div className="spinner-border text-primary" role="status">
              <span className="visually-hidden">{t('LOADING')}...</span>
            </div>
          </div>
        )}
        <div className="result-search-summary">
          <Markdown>
            {summary_result}
          </Markdown>
        </div>
        {resource_list.map((item, index) => (
          <div key={index}>
            <SearchResultItem data={item} />
          </div>
        ))}
      </div>
    </>
  );
};

export default BoxSearchResult;
