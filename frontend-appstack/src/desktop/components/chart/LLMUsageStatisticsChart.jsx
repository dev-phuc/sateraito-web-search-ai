// Framework import
import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useParams } from "react-router-dom";
import moment from 'moment';

// Zustand store
import useStoreLLMUsage from "@/store/llm_usage";

// Hook components
import useTheme from "@/hooks/useTheme";

// Context components

// Library imports
// Library IU imports
import ApexCharts from "apexcharts";
import { Container, Spinner } from "react-bootstrap";

// Constant value
import { randomString } from "@/utils";

// Components
import MakerLoading from "../MakerLoading";

// Define the component
const LLMUsageStatisticsChart = ({ }) => {
  // Use default
  const { t } = useTranslation();
  const { tenant, app_id } = useParams();
  const { showNotice } = useTheme();

  // Zustand store
  const { isLoading, llmUsage, llmUsageLastMonth, fetchLLMUsage, fetchLLMUsageLastMonth } = useStoreLLMUsage();

  // state
  const [timeFrame, setTimeFrame] = useState('month');
  const [chartType, setChartType] = useState('area');
  const [dataTableShow, setDataTableShow] = useState([]);

  const idChart = `llm-usage-chart-${randomString(6)}`;

  // Handler
  const handlerLoadData = async () => {
    const { success, message } = await fetchLLMUsage(tenant, app_id, timeFrame);
    if (!success) {
      showNotice('danger', t(message));
    }
  }
  const handlerLoadDataLastMonth = async () => {
    const { success, message } = await fetchLLMUsageLastMonth(tenant, app_id);
    if (!success) {
      showNotice('danger', t(message));
    }
  }

  useEffect(() => {
    if (!isLoading && !llmUsage) {
      handlerLoadData();
    }
    if (!llmUsageLastMonth) {
      handlerLoadDataLastMonth();
    }
  }, [timeFrame]);

  useEffect(() => {
    // Helper function to process a usage list (reused for both months)
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

    // Process current month data
    const currentMonthData = processUsageList(llmUsage?.usage_list);

    // Process last month data
    const lastMonthData = processUsageList(llmUsageLastMonth?.usage_list);

    // Update dataTableShow (combine both, sort by timestamp descending)
    const combinedData = [...currentMonthData, ...lastMonthData];
    combinedData.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    setDataTableShow(combinedData);

    // Prepare chart data for two series
    const currentMonthChartData = currentMonthData.map((item) => ({
      x: item.timestamp.getTime(),
      y: item.request_count,
    }));
    const lastMonthChartData = lastMonthData.map((item) => ({
      x: item.timestamp.getTime(),
      y: item.request_count,
    }));

    // Clear existing chart container
    const chartContainer = document.querySelector(`#${idChart}`);
    if (chartContainer) {
      chartContainer.innerHTML = '';
    }

    const seriesOptions = [{
      name: t('LABEL_CURRENT_MONTH_REQUESTS'),
      data: currentMonthChartData,
    }];
    if (lastMonthChartData.length > 0) {
      seriesOptions.push({
        name: t('LABEL_LAST_MONTH_REQUESTS'),
        data: lastMonthChartData,
      });
    }

    // Chart options with two series
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
  }, [chartType, llmUsage, llmUsageLastMonth]);

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

export default LLMUsageStatisticsChart;
