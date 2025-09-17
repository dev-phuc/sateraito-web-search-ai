// Framework import
import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useParams } from "react-router-dom";
import { Helmet } from "react-helmet-async";

// moment
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

// Components
import OverviewUsageBoxPanel from "@/desktop/components/panel/OverviewUsageBox";

// Define the component
const LLMUsageAdminConsolePage = () => {
  // Use default
  const { t } = useTranslation();
  const { tenant, app_id } = useParams();

  const CHART_TYPE = [
    { value: 'bar', label: t('TXT_BAR_CHART') },
    { value: 'area', label: t('TXT_AREA_CHART') },
    { value: 'line', label: t('TXT_LINE_CHART') },
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
  const [timeFrame, setTimeFrame] = useState('month');
  const [chartType, setChartType] = useState('bar');
  const [dataTableShow, setDataTableShow] = useState([]);

  useEffect(() => {
    if (!isLoading) {
      fetchLLMUsage(tenant, app_id, timeFrame);
    }
  }, [timeFrame]);

  useEffect(() => {
    const { usage_list: rawUsageList } = llmUsage || {};
    const usageList = rawUsageList || [];

    // Sort usage list by timestamp
    const usageListSorted = [...usageList].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

    // Group by hour and count requests
    const usageMap = {};
    usageListSorted.forEach((item) => {
      const dateKey = moment(item.timestamp).format('YYYY-MM-DD HH:00');
      usageMap[dateKey] = {
        model_name: (usageMap[dateKey]?.model_name || []).concat(item.model_name || []),
        total_requests: (usageMap[dateKey]?.total_requests || 0) + 1,
        prompt_length: (usageMap[dateKey]?.prompt_length || 0) + (item.prompt_length || 0),
        completion_length: (usageMap[dateKey]?.completion_length || 0) + (item.completion_length || 0),
        total_length: (usageMap[dateKey]?.total_length || 0) + (item.total_length || 0),
      }
    });

    // Convert to sorted array of data points
    const dataShow = Object.keys(usageMap)
      .sort()
      .map((date) => ({
        timestamp: moment(date).toDate(),
        model_name: [...new Set(usageMap[date].model_name)],
        total_length: usageMap[date].total_length,
        prompt_length: usageMap[date].prompt_length,
        completion_length: usageMap[date].completion_length,
        request_count: usageMap[date].total_requests,
      }));

    // Set data show state
    let dataTableShow = [...dataShow];
    // Sort by timestamp descending
    dataTableShow.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    setDataTableShow(dataTableShow);

    // Prepare chart data
    const chartData = dataShow.map((item) => ({
      x: item.timestamp.getTime(),
      y: item.request_count,
    }));

    // Clear existing chart container
    const chartContainer = document.querySelector("#chart-llm-usage");
    if (chartContainer) {
      chartContainer.innerHTML = '';
    }

    // Chart options
    const options = {
      chart: {
        type: chartType,
        height: 400,
      },
      series: [{
        name: t('LABEL_TOTAL_REQUESTS'),
        data: chartData,
      }],
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

    // Render chart if data exists
    let chart = null;
    if (dataShow.length > 0) {
      chart = new ApexCharts(chartContainer, options);
      chart.render();
    }

    // Cleanup on unmount or dependency change
    return () => {
      if (chart) {
        chart.destroy();
      }
    };
  }, [chartType, llmUsage]);

  if (isLoading && !llmUsage) {
    return <div>Loading...</div>;
  }

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
            {(dataTableShow.length === 0) && !isLoading && (
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

        {/* Usage breakdown */}
        <Container fluid className="p-0 mt-4">
          <div className="box p-3 bg-white rounded">
            <div className="mb-3">
              <h5 className="">{t('LABEL_LLM_USAGE_BREAKDOWN')}</h5>
              <p>{t('MSG_LLM_USAGE_BREAKDOWN_INFO')}</p>
            </div>

            {/* Table of dataTableShow */}
            <div className="table-responsive">
              <table className="table table-bordered table-hover">
                <thead>
                  <tr>
                    <th>{t('LABEL_TIMESTAMP')}</th>
                    <th>{t('LABEL_MODEL_NAME')}</th>
                    <th>{t('LABEL_PROMPT_LENGTH')}</th>
                    <th>{t('LABEL_COMPLETION_LENGTH')}</th>
                    <th>{t('LABEL_TOTAL_LENGTH')}</th>
                    <th>{t('LABEL_TOTAL_REQUESTS')}</th>
                    
                  </tr>
                </thead>
                <tbody>
                  {dataTableShow.length > 0 ? (
                    dataTableShow.map((item, index) => (
                      <tr key={index}>
                        <td>{moment(item.timestamp).format('YYYY-MM-DD HH:mm:ss')}</td>
                        <td>{item.model_name.join(', ')}</td>
                        <td>{item.prompt_length}</td>
                        <td>{item.completion_length}</td>
                        <td>{item.total_length}</td>
                        <td>{item.request_count || 1}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="6" className="text-center">{t('MSG_DATA_LLM_USAGE_NO_DATA')}</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </Container>

      </Container>

    </>
  );
};

export default LLMUsageAdminConsolePage;
