// Framework import
import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useParams } from "react-router-dom";
import { Helmet } from "react-helmet-async";

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

// Components
import OverviewUsageBoxPanel from "@/desktop/components/panel/OverviewUsageBox";

// Define the component
const LLMUsageAdminConsolePage = () => {
  // Use default
  const { t } = useTranslation();
  const { tenant, app_id } = useParams();

  const CHART_TYPE = [
    { value: 'area', label: t('TXT_AREA_CHART') },
    { value: 'line', label: t('TXT_LINE_CHART') },
    { value: 'bar', label: t('TXT_BAR_CHART') },
  ];
  const TIME_FRAME_LIST = [
    { value: 'all', label: t('TXT_ALL_TIME') },
    { value: 'day', label: t('TXT_TODAY') },
    { value: 'week', label: t('TXT_THIS_WEEK') },
    { value: 'month', label: t('TXT_THIS_MONTH') },
    { value: 'last_month', label: t('TXT_LAST_MONTH') },
  ];

  // Zustand store
  const { isLoading, llmUsage, fetchLLMUsage } = useStoreLLMUsage();

  // state
  const [timeFrame, setTimeFrame] = useState('day');
  const [chartType, setChartType] = useState('area');

  useEffect(() => {
    if (!isLoading) {
      fetchLLMUsage(tenant, app_id, timeFrame);
    }
  }, [timeFrame]);

  useEffect(() => {
    let { usage_list } = llmUsage || {};
    if (!usage_list) {
      usage_list = [];
    }

    let usageListSorted = [...usage_list];
    usageListSorted.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

    let dataShow = [];
    if (timeFrame === 'day') {
      let usageMap = {};

      usageListSorted.forEach((item) => {
        const hourAndMinute = new Date(item.timestamp);
        hourAndMinute.setSeconds(0, 0);
        const hourKey = hourAndMinute.toISOString();
        if (!usageMap[hourKey]) {
          usageMap[hourKey] = 0;
        }
        // usageMap[hourKey] += item.total_length;
        usageMap[hourKey] += 1; // Count each request
      });

      console.log(usageMap);

      // Convert to array
      dataShow = Object.keys(usageMap).map((hour) => ({
        timestamp: new Date(hour).toISOString(),
        total_length: usageMap[hour],
      }));
      usage_list = dataShow;

    } else {
      // Total usage per day
      let usageMap = {};
      usageListSorted.forEach((item) => {
        const dateKey = new Date(item.timestamp).toISOString().split('T')[0];
        if (!usageMap[dateKey]) {
          usageMap[dateKey] = 0;
        }
        // usageMap[dateKey] += item.total_length;
        usageMap[dateKey] += 1; // Count each request
      });

      // Convert to array
      dataShow = Object.keys(usageMap).map((date) => ({
        timestamp: new Date(date).toISOString(),
        total_length: usageMap[date],
      }));
      usage_list = dataShow;
    }

    // Check already chart and destroy
    const existingChart = document.querySelector("#chart-llm-usage .apexcharts-canvas");
    if (existingChart) {
      existingChart.parentNode.removeChild(existingChart);
    }

    const options = {
      chart: {
        type: chartType,
        height: 400,
      },
      series: [{
        name: t('LABEL_TOTAL_REQUESTS'),
        data: usage_list.map((item) => ({
          x: new Date(item.timestamp),
          y: item.total_length
        }))
      }],
      xaxis: {
        type: 'datetime',
        title: {
          text: t('LABEL_TIMESTAMP')
        }
      },
      yaxis: {
        title: {
          text: t('LABEL_TOTAL_REQUESTS')
        }
      },
    };

    if (usage_list) {
      const chart = new ApexCharts(document.querySelector("#chart-llm-usage"), options);
      chart.render();
      return () => {
        chart.destroy();
      };
    }
  }, [chartType, llmUsage]);

  if (isLoading && !llmUsage) {
    return <div>Loading...</div>;
  }

  let { llm_quota_last_reset, llm_quota_monthly, llm_quota_used, llm_quota_remaining, usage_list } = llmUsage;

  // Return component
  return (
    <>
      <Helmet>
        <title>{t("PAGE_TITLE_LLM_USAGE_MANAGER")}</title>
      </Helmet>

      <Container fluid className="p-0">
        {/* Overview box panel */}
        <OverviewUsageBoxPanel />

        {/* Chart apexcharts show usage_list*/}
        <div className="box p-3 bg-white rounded">
          {/* Header */}
          <div className="d-flex align-items-center justify-content-between mb-3">
            <div className="d-flex align-items-center header-left">
              {/* </div>

            <div className="header-right"> */}
              <div className="d-flex align-items-center">
                <label className="me-2 mb-0">{t('LABEL_TIME_FRAME')}:</label>
                <select className="form-select me-3" style={{ width: '150px' }} value={timeFrame} onChange={(e) => setTimeFrame(e.target.value)}>
                  {TIME_FRAME_LIST.map((frame) => (
                    <option key={frame.value} value={frame.value}>{frame.label}</option>
                  ))}
                </select>
                <label className="me-2 mb-0">{t('LABEL_CHART_TYPE')}:</label>
                <select className="form-select" style={{ width: '150px' }} value={chartType} onChange={(e) => setChartType(e.target.value)}>
                  {CHART_TYPE.map((type) => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="wrap-chart position-relative">
            <div id="chart-llm-usage">
              {/* Chart will be rendered here by ApexCharts */}
            </div>
            {/* Empty */}
            {(!usage_list || usage_list.length === 0) && !isLoading && (
              <div className="position-absolute top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center">
                <div className="text-center">
                  <div className="h1 mt-2 text-muted small">{t('MSG_DATA_LLM_USAGE_NO_DATA')}</div>
                </div>
              </div>
            )}
            {/* Marker loading */}
            {isLoading && (
              <div className="position-absolute top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center bg-white bg-opacity-75">
                <div className="text-center">
                  <Spinner animation="border" variant="primary" />
                  <div className="mt-2 text-muted small">{t('MSG_DATA_LLM_USAGE_LOADING')}</div>
                </div>
              </div>
            )}
          </div>
        </div>

      </Container>

    </>
  );
};

export default LLMUsageAdminConsolePage;
