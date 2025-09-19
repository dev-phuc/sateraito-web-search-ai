// Framework import
import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useParams } from "react-router-dom";
import moment from 'moment';

// Zustand store
import useStoreLLMUsage from "@/store/llm_usage";

// Hook components

// Context components

// Library imports
// Library IU imports
import ApexCharts from "apexcharts";

// Constant value
import { randomString } from "@/utils";

// Components
import MakerLoading from "../MakerLoading";

// Define the component
const LLMClientWebsiteUsageStatisticsChart = ({ }) => {
  // Use default
  const { t } = useTranslation();
  const { tenant, app_id } = useParams();

  // Zustand store
  const { isLoading, llmUsage, fetchLLMUsage } = useStoreLLMUsage();

  // state
  const [timeFrame, setTimeFrame] = useState('month');
  const [chartType, setChartType] = useState('line');
  const [dataTableShow, setDataTableShow] = useState([]);

  const idChart = `llm-client-website-usage-chart-${randomString(5)}`;

  // useEffect(() => {
  //   if (!isLoading && !llmUsage) {
  //     fetchLLMUsage(tenant, app_id, timeFrame);
  //   }
  // }, [timeFrame]);

  /**
  llmUsage = [
    {
        "client_domain": "https://elearning.test.plt.pro.vn",
        "completion_length": 1604,
        "model_name": "sonar",
        "prompt_length": 3,
        "timestamp": "2025-09-18 11:07:29",
        "total_length": 1607
    },
    {
        "client_domain": "https://store.test.plt.pro.vn",
        "completion_length": 1604,
        "model_name": "sonar",
        "prompt_length": 3,
        "timestamp": "2025-09-18 11:07:29",
        "total_length": 1607
    },
    {
        "client_domain": "https://ecommerce.test.plt.pro.vn",
        "completion_length": 1604,
        "model_name": "sonar",
        "prompt_length": 3,
        "timestamp": "2025-09-18 11:07:29",
        "total_length": 1607
    },
    ...
  ]
  */

  useEffect(() => {
    // Helper function to process a usage list (reused for both cases)
    const processUsageList = (usageList) => {
      if (!usageList || usageList.length === 0) return [];
      const sorted = [...usageList].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
      const usageMap = {};
      sorted.forEach((item) => {
        const dateKey = moment(item.timestamp).format('YYYY-MM-DD HH:00');
        usageMap[dateKey] = {
          model_name: (usageMap[dateKey]?.model_name || []).concat(item.model_name || []),
          total_requests: (usageMap[dateKey]?.total_requests || 0) + 1,
          prompt_length: (usageMap[dateKey]?.prompt_length || 0) + (item.prompt_length || 0),
          completion_length: (usageMap[dateKey]?.completion_length || 0) + (item.completion_length || 0),
          total_length: (usageMap[dateKey]?.total_length || 0) + (item.total_length || 0),
        };
      });
      return Object.keys(usageMap)
        .sort()
        .map((date) => ({
          timestamp: moment(date).toDate(),
          model_name: [...new Set(usageMap[date].model_name)],
          total_length: usageMap[date].total_length,
          prompt_length: usageMap[date].prompt_length,
          completion_length: usageMap[date].completion_length,
          request_count: usageMap[date].total_requests,
        }));
    };

    const processUsageListByDomain = (usageList) => {
      if (!usageList || usageList.length === 0) return {};
      const domainMap = {};
      usageList.forEach((item) => {
        const domain = item.client_domain || 'Unknown';
        if (!domainMap[domain]) {
          domainMap[domain] = [];
        }
        domainMap[domain].push(item);
      });

      // For each domain, group by timestamp (hour) and count request_count
      const result = {};
      Object.keys(domainMap).forEach((domain) => {
        const sorted = domainMap[domain].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
        const timeMap = {};
        sorted.forEach((item) => {
          const dateKey = moment(item.timestamp).format('YYYY-MM-DD HH:00');
          timeMap[dateKey] = (timeMap[dateKey] || 0) + 1; // Increase request_count for each hour
        });
        result[domain] = Object.keys(timeMap)
          .sort()
          .map((date) => ({
            x: moment(date).toDate().getTime(),
            y: timeMap[date],
          }));
      });
      return result;
    };

    // Process current month's data by domain
    const domainData = processUsageListByDomain(llmUsage?.usage_list);

    // Update dataTableShow (keep current logic if needed, or adjust if you want to display by domain)
    const currentMonthData = processUsageList(llmUsage?.usage_list); // Keep old function if needed for table
    const combinedData = [...currentMonthData];
    combinedData.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    setDataTableShow(combinedData);

    // Prepare seriesOptions: one series for each client_domain
    const seriesOptions = Object.keys(domainData).map((domain) => ({
      name: domain,
      data: domainData[domain],
    }));

    // Clear existing chart container
    const chartContainer = document.querySelector(`#${idChart}`);
    if (chartContainer) {
      chartContainer.innerHTML = '';
    }

    // Chart options with multiple series
    const options = {
      chart: {
        type: chartType,
        height: 400,
      },
      series: seriesOptions,
      xaxis: {
        type: 'datetime',
        title: {
          text: t('LABEL_TIMESTAMP'),
        },
        labels: {
          datetimeUTC: false,
        },
      },
      yaxis: {
        title: {
          text: t('LABEL_TOTAL_REQUESTS'),
        },
      },
    };

    // Render chart if there is data
    let chart = new ApexCharts(chartContainer, options);
    chart.render();

    // Cleanup
    return () => {
      if (chart) {
        chart.destroy();
      }
    };
  }, [chartType, llmUsage]);

  // Return component
  return (
    <>
      <div className="wrap-chart position-relative">
        <div id={idChart} className="chart">
          {/* Chart will be rendered here by ApexCharts */}
        </div>
        
        {/* Empty */}
        {(!isLoading && dataTableShow.length === 0) && (
          <div className="position-absolute top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center">
            <div className="text-center">
              <div className="h1 mt-2 text-muted small">{t('MSG_DATA_LLM_USAGE_NO_DATA')}</div>
            </div>
          </div>
        )}

        {/* Loading */}
        {isLoading && <MakerLoading />}

      </div>
    </>
  );
};

export default LLMClientWebsiteUsageStatisticsChart;
