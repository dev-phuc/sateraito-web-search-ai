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
import { Row, Col, Container, Spinner } from "react-bootstrap";

// Constant value

// Components
import Loader from "@/desktop/components/Loader";
import OverviewUsageBoxPanel from "@/desktop/components/box/OverviewUsageBoxNew";

// Define the component
const LLMUsageAdminConsolePage = () => {
  // Use default
  const { t } = useTranslation();
  const { tenant, app_id } = useParams();
  const { showNotice } = useTheme();

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

  // Handler
  const handlerLoadData = async () => {
    const { success, message } = await fetchLLMUsage(tenant, app_id, timeFrame);
    if (!success) {
      showNotice('danger', t(message));
    }
  }

  useEffect(() => {
    if (!isLoading) {
      handlerLoadData();
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
    return <Loader />;
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
          <Row>
            <Col className="col-md-6 mb-4 mb-md-0">
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
            </Col>
            {dataTableShow.length > 0 && (
              <Col className="col-md-6">
                <div className="row g-3">
                  <div className="col-md-6">
                    <div className="card border-0 shadow-sm static-card" style={{ backgroundColor: '#f8f9ff' }}>
                      <div className="card-body text-center p-3">
                        <div >
                          <div className="rounded-circle d-inline-flex align-items-center justify-content-center mb-2"
                            style={{ width: '48px', height: '48px', backgroundColor: '#e3f2fd' }}>
                            <i className="mdi mdi-pencil-outline text-primary mdi-24px"></i>
                          </div>
                        </div>
                        <small className="text-muted fw-medium d-block mb-2">{t('LABEL_TOTAL_PROMPT_TOKENS') || 'Prompt Tokens'}</small>
                        <div className="h5 mb-0 fw-bold text-primary">
                          {dataTableShow.reduce((sum, item) => sum + item.prompt_length, 0).toLocaleString()}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="card border-0 shadow-sm static-card" style={{ backgroundColor: '#fff8f0' }}>
                      <div className="card-body text-center p-3">
                        <div>
                          <div className="rounded-circle d-inline-flex align-items-center justify-content-center mb-2"
                            style={{ width: '48px', height: '48px', backgroundColor: '#fff3e0' }}>
                            <i className="mdi mdi-robot-outline text-warning mdi-24px"></i>
                          </div>
                        </div>
                        <small className="text-muted fw-medium d-block mb-2">{t('LABEL_TOTAL_COMPLETION_TOKENS') || 'Completion Tokens'}</small>
                        <div className="h5 mb-0 fw-bold text-warning">
                          {dataTableShow.reduce((sum, item) => sum + item.completion_length, 0).toLocaleString()}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="card border-0 shadow-sm static-card" style={{ backgroundColor: '#f0fff4' }}>
                      <div className="card-body text-center p-3">
                        <div >
                          <div className="rounded-circle d-inline-flex align-items-center justify-content-center mb-2"
                            style={{ width: '48px', height: '48px', backgroundColor: '#e8f5e8' }}>
                            <i className="mdi mdi-chart-line text-success mdi-24px"></i>
                          </div>
                        </div>
                        <small className="text-muted fw-medium d-block mb-2">{t('LABEL_GRAND_TOTAL_TOKENS') || 'Total Tokens'}</small>
                        <div className="h5 mb-0 fw-bold text-success">
                          {dataTableShow.reduce((sum, item) => sum + item.total_length, 0).toLocaleString()}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="card border-0 shadow-sm static-card" style={{ backgroundColor: '#fff5f5' }}>
                      <div className="card-body text-center p-3">
                        <div >
                          <div className="rounded-circle d-inline-flex align-items-center justify-content-center mb-2"
                            style={{ width: '48px', height: '48px', backgroundColor: '#ffebee' }}>
                            <i className="mdi mdi-flash text-danger mdi-24px"></i>
                          </div>
                        </div>
                        <small className="text-muted fw-medium d-block mb-2">{t('LABEL_TOTAL_API_CALLS') || 'API Calls'}</small>
                        <div className="h5 mb-0 fw-bold text-danger">
                          {dataTableShow.reduce((sum, item) => sum + (item.request_count || 1), 0).toLocaleString()}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </Col>
            )}

          </Row>

        </div>

        {/* Usage breakdown */}
        <Container fluid className="p-0 mt-4 usage-breakdown-container">
          <div className=" card-custom  p-2">
            {/* Header Section */}
            <div className="bg-gradient-primary rounded-top">
              <div className="d-flex align-items-center justify-content-between">
                <div>
                  <h4 className="mb-0 fw-bold text-dark">{t('LABEL_LLM_USAGE_BREAKDOWN')}</h4>
                  <p className="mb-0 opacity-75 small">{t('MSG_LLM_USAGE_BREAKDOWN_INFO')}</p>
                </div>
                <div className="text-end">
                  <div className="bg-white bg-opacity-20 rounded px-3 py-2">
                    <div className="small opacity-75">{t('LABEL_TOTAL_RECORDS')}</div>
                    <div className="h6 mb-0 fw-bold">{dataTableShow.length}</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Table Section */}
            <Row>
              {/* Table Footer with Statistics */}
              <Col className="table-responsive col-md-12">
                <table className="table table-striped table-hover mb-0 ">
                  <thead >
                    <tr>
                      <th className="border-0 py-3">
                        <i className="mdi mdi-clock-outline me-2"></i>
                        {t('LABEL_TIMESTAMP')}
                      </th>
                      <th className="border-0 py-3">
                        <i className="mdi mdi-robot-outline me-2"></i>
                        {t('LABEL_MODEL_NAME')}
                      </th>
                      <th className="border-0 py-3 text-center">
                        <i className="mdi mdi-message-text-outline me-2"></i>
                        {t('LABEL_PROMPT_LENGTH')}
                      </th>
                      <th className="border-0 py-3 text-center">
                        <i className="mdi mdi-reply-outline me-2"></i>
                        {t('LABEL_COMPLETION_LENGTH')}
                      </th>
                      <th className="border-0 py-3 text-center">
                        <i className="mdi mdi-calculator me-2"></i>
                        {t('LABEL_TOTAL_LENGTH')}
                      </th>
                      <th className="border-0 py-3 text-center">
                        <i className="mdi mdi-send-outline me-2"></i>
                        {t('LABEL_TOTAL_REQUESTS')}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {dataTableShow.length > 0 ? (
                      dataTableShow.map((item, index) => (
                        <tr key={index} className="align-middle">
                          <td className="py-3">
                            <div className="d-flex ">
                              <span className="fw-medium">{moment(item.timestamp).format('YYYY-MM-DD')} {moment(item.timestamp).format('HH:mm:ss')}</span>
                            </div>
                          </td>
                          <td className="py-3">
                            <div className="d-flex flex-wrap gap-1">
                              {item.model_name.map((model, idx) => (
                                // <span key={idx} className="badge bg-secondary bg-opacity-10 text-dark border">
                                //   {model}
                                // </span>
                                <span key={idx} className='badge ai-model chip'><i class="mdi mdi-robot "></i>{model}</span>

                              ))}
                            </div>
                          </td>
                          <td className="py-3 text-left">
                            <span className="badge text-info bg-opacity-20  px-3 py-2 rounded-pill">
                              {item.prompt_length.toLocaleString()}
                            </span>
                          </td>
                          <td className="py-3 text-center">
                            <span className="badge bg-white text-success bg-opacity-20 px-3 py-2 rounded-pill">
                              {item.completion_length.toLocaleString()}
                            </span>
                          </td>
                          <td className="py-3 text-center">
                            <span className="badge bg-white text-primary bg-opacity-20 px-3 py-2 rounded-pill fw-bold">
                              {item.total_length.toLocaleString()}
                            </span>
                          </td>
                          <td className="py-3 text-center">
                            <span className="badge bg-white text-warning bg-opacity-20  px-3 py-2 rounded-pill">
                              {(item.request_count || 1).toLocaleString()}
                            </span>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="6" className="text-center py-5">
                          <div className="d-flex flex-column align-items-center justify-content-center">
                            <i className="mdi mdi-chart-bar mdi-48px text-muted mb-3 opacity-50"></i>
                            <h6 className="text-muted mb-2">{t('MSG_DATA_LLM_USAGE_NO_DATA')}</h6>
                            <small className="text-muted opacity-75">
                              {t('MSG_TRY_DIFFERENT_TIME_FRAME') || 'Try selecting a different time frame'}
                            </small>
                          </div>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </Col>
            </Row>
          </div>
        </Container>

      </Container>

    </>
  );
};

export default LLMUsageAdminConsolePage;
