// Framework import
import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate, useParams } from 'react-router-dom';

// Hook components
import useTheme from "@/hooks/useTheme";

// Context components

// Library imports

// Library IU imports
import Markdown from 'react-markdown'

// Zustand

// Constant value

// Components

// API

// Utils
import { getPageInfoByUrl } from "@/request/sateraitoUtils";

// Define the component
const SearchResultItem = ({ data }) => {
  // Use default
  const { t } = useTranslation();
  const { tenant, app_id } = useParams();

  const [pageInfo, setPageInfo] = useState({
    favicon: data.favicon || 'https://www.google.com/s2/favicons?domain=example.com',
    url: data.url || '',
    title: data.title || '',
    description: data.snippet || '',
  });

  const loadPageInfo = async (url) => {
    try {
      const info = await getPageInfoByUrl(url);

      // Update only favicon
      if (info.favicon_url) {
        setPageInfo(prev => ({
          ...prev,
          favicon: info.favicon_url,
        }));
      }

    } catch (error) {
      console.error('Failed to load page info:', error);
    }
  };

  useEffect(() => {
    if (data && data.url) {
      // loadPageInfo(data.url);
    }
  }, [data]);

  // Return component
  return (
    <div className="result-search-item">
      <div className="result-search-item-header d-flex align-items-center">
        {pageInfo.favicon && <img src={pageInfo.favicon} alt="Favicon" className="result-search-favicon" />}
        <a href={pageInfo.url} target="_blank" rel="noopener noreferrer" className="result-search-title">{pageInfo.title}</a>
      </div>
      <div className="result-search-item-description">
        {pageInfo.description}
      </div>
    </div>
  );
};

export default SearchResultItem;
