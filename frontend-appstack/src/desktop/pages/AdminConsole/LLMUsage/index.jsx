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
import { Row, Col, Container, Spinner,Table } from "react-bootstrap";

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
  
  // Pagination states
  const optionsLimit = [5, 10, 20, 50, 100];
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(optionsLimit[2]); // Default 20
  const [listPages, setListPages] = useState([]);

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

    // Reset to first page when data changes
    setPage(1);

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

  // Pagination effect
  useEffect(() => {
    // Generate list pages
    // Show max 10 pages, with "..." if more than 10 pages
    const totalPages = Math.ceil(dataTableShow.length / limit);
    let pages = [];
    if (totalPages <= 10) {
      pages = Array.from({ length: totalPages }, (_, i) => i + 1);
    }
    else {
      if (page <= 6) {
        pages = [...Array(8).keys()].map(i => i + 1);
        pages.push('...');
        pages.push(totalPages);
      }
      else if (page >= totalPages - 5) {
        pages = [1, '...'];
        pages = pages.concat([...Array(8).keys()].map(i => totalPages - 8 + i + 1));
      }
      else {
        pages = [1, '...'];
        pages = pages.concat([...Array(5).keys()].map(i => page - 2 + i + 1));
        pages.push('...');
        pages.push(totalPages);
      }
    }

    setListPages(pages);
  }, [dataTableShow, page, limit]);

  // Get paginated data
  const getPaginatedData = () => {
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    return dataTableShow.slice(startIndex, endIndex);
  };

  const paginatedData = getPaginatedData();
  const totalPages = Math.ceil(dataTableShow.length / limit);
  const isHaveMore = page < totalPages;

  if (isLoading && !llmUsage) {
    return <Loader />;
  }

  // Return component
  return (
    <>
      <Helmet>
        <title>{t("PAGE_TITLE_LLM_USAGE_MANAGER")}</title>
      </Helmet>
      


      <Container fluid className="p-0 usage-page">
        {/* Overview box panel */}
        <OverviewUsageBoxPanel />

        {/* Chart apexcharts show usage_list*/}
        <div className="card-custom">
          <div className="card  mb-0 shadow-none">
            <div className="card-header  border-0">
              <div className="d-flex align-items-center justify-content-between">
                <div>
                  <h5 className="mb-1 fw-bold text-dark">
                    <i className="mdi mdi-chart-line me-2"></i>
                    {t('LABEL_LLM_USAGE_ANALYTICS') || 'LLM Usage Analytics'}
                  </h5>
                  <p className="mb-0 opacity-75 small">{t('MSG_TRACK_YOUR_LLM_USAGE') || 'Track and analyze your LLM usage patterns'}</p>
                  {/* Compact Filter Chips Section */}
                </div>
                <div className="d-flex align-items-center flex-wrap gap-3 mb-4  rounded-3">
                  {/* Time Frame Filter Chips */}
                  <div className="d-flex align-items-center flex-wrap gap-2">
                    <div className="d-flex align-items-center me-2">
                      <i className="mdi mdi-calendar-range me-1 text-primary" style={{ fontSize: '18px' }}></i>
                      <span className="text-dark fw-medium" style={{ fontSize: '0.85rem' }}>{t('LABEL_TIME_FRAME')}:</span>
                    </div>
                    {TIME_FRAME_LIST.map((frame) => (
                      <button
                        key={frame.value}
                        type="button"
                        className={`btn btn-sm rounded-pill border-0 quick-filter-chip position-relative ${timeFrame === frame.value
                          ? 'text-white shadow-sm'
                          : 'btn-outline-primary bg-white text-primary border'
                          }`}
                        style={{
                          fontSize: '0.75rem',
                          padding: '4px 10px',
                          fontWeight: '500',
                          lineHeight: '1.2',
                          background: timeFrame === frame.value
                            ? 'linear-gradient(135deg, #4dabf7 0%, #339af0 100%)'
                            : 'white',
                          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                          borderColor: timeFrame === frame.value ? 'transparent' : '#4dabf7'
                        }}
                        onClick={() => setTimeFrame(frame.value)}
                        onMouseEnter={(e) => {
                          if (timeFrame !== frame.value) {
                            e.target.style.transform = 'translateY(-1px)';
                            e.target.style.boxShadow = '0 2px 8px rgba(77, 171, 247, 0.3)';
                            e.target.style.backgroundColor = '#e3f2fd';
                          }
                        }}
                        onMouseLeave={(e) => {
                          if (timeFrame !== frame.value) {
                            e.target.style.transform = 'translateY(0)';
                            e.target.style.boxShadow = 'none';
                            e.target.style.backgroundColor = 'white';
                          }
                        }}
                      >
                        {frame.value === 'day' && (
                          <i className="mdi mdi-calendar-today me-1" style={{ fontSize: '0.65rem' }}></i>
                        )}
                        {frame.value === 'week' && (
                          <i className="mdi mdi-calendar-week me-1" style={{ fontSize: '0.65rem' }}></i>
                        )}
                        {frame.value === 'month' && (
                          <i className="mdi mdi-calendar-month me-1" style={{ fontSize: '0.65rem' }}></i>
                        )}
                        {frame.value === 'last_month' && (
                          <i className="mdi mdi-calendar-month-outline me-1" style={{ fontSize: '0.65rem' }}></i>
                        )}
                        {frame.value === 'all' && (
                          <i className="mdi mdi-calendar-multiselect me-1" style={{ fontSize: '0.65rem' }}></i>
                        )}
                        {timeFrame === frame.value && (
                          <i className="mdi mdi-check me-1" style={{ fontSize: '0.65rem' }}></i>
                        )}
                        {frame.label}
                      </button>
                    ))}
                  </div>

                  {/* Separator */}
                  <div className="vr align-self-stretch mx-2" style={{ opacity: 0.3 }}></div>

                  {/* Chart Type Filter Chips */}
                  <div className="d-flex align-items-center flex-wrap gap-2">
                    <div className="d-flex align-items-center me-2">
                      <i className="mdi mdi-chart-bar me-1 text-success" style={{ fontSize: '18px' }}></i>
                      <span className="text-dark fw-medium" style={{ fontSize: '0.85rem' }}>{t('LABEL_CHART_TYPE')}:</span>
                    </div>
                    {CHART_TYPE.map((type) => (
                      <button
                        key={type.value}
                        type="button"
                        className={`btn btn-sm rounded-pill border-0 quick-filter-chip position-relative ${chartType === type.value
                          ? 'text-white shadow-sm'
                          : 'btn-outline-success bg-white text-success border'
                          }`}
                        style={{
                          fontSize: '0.75rem',
                          padding: '4px 10px',
                          fontWeight: '500',
                          lineHeight: '1.2',
                          background: chartType === type.value
                            ? 'linear-gradient(135deg, #51cf66 0%, #40c057 100%)'
                            : 'white',
                          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                          borderColor: chartType === type.value ? 'transparent' : '#51cf66'
                        }}
                        onClick={() => setChartType(type.value)}
                        onMouseEnter={(e) => {
                          if (chartType !== type.value) {
                            // e.target.style.transform = 'translateY(-1px)';
                            // e.target.style.boxShadow = '0 2px 8px rgba(81, 207, 102, 0.3)';
                            // e.target.style.backgroundColor = '#e8f5e8';
                          }
                        }}
                        onMouseLeave={(e) => {
                          if (chartType !== type.value) {
                            // e.target.style.transform = 'translateY(0)';
                            // e.target.style.boxShadow = 'none';
                            // e.target.style.backgroundColor = 'white';
                          }
                        }}
                      >

                        {type.value === 'bar' && (
                          <i className="mdi mdi-chart-bar me-1" style={{ fontSize: '0.65rem' }}></i>
                        )}
                        {type.value === 'area' && (
                          <i className="mdi mdi-chart-areaspline me-1" style={{ fontSize: '0.65rem' }}></i>
                        )}
                        {type.value === 'line' && (
                          <i className="mdi mdi-chart-line me-1" style={{ fontSize: '0.65rem' }}></i>
                        )}
                        {type.label}
                        {chartType === type.value && (
                          <i className="mdi mdi-check-circle ms-1" style={{ fontSize: '0.65rem' }}></i>
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="card-body p-4 pb-0">

            <Row>
              <Col className="col-md-7 mb-4 mb-md-0">
                <div className="wrap-chart position-relative">
                  <div id="chart-llm-usage">
                    {/* Chart will be rendered here by ApexCharts */}
                  </div>
                  {/* Empty */}
                  {/* {(dataTableShow.length === 0) && !isLoading && (
                    <div className="position-absolute top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center">
                      <div className="text-center">
                        <div className="h1 mt-2 text-muted small">{t('MSG_DATA_LLM_USAGE_NO_DATA')}</div>
                      </div>
                    </div>
                  )} */}
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
                <Col className="col-md-5">
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
          </div>

          {/* Usage breakdown */}
          <Container fluid className="p-0  usage-breakdown-container">
            <div className="  p-2">
              {/* Header Section */}
              <div className=" rounded-top d-none">
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
                <Col className="table-responsive col-md-12 table-statistics">
                  <Table className="table table-striped borderless table-hover mb-0  " borderless striped>
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
                      {paginatedData.length > 0 ? (
                        paginatedData.map((item, index) => (
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
                                  <span key={idx} className='badge ai-model chip m-0'><i className="mdi mdi-robot "></i>{model}</span>

                                ))}
                              </div>
                            </td>
                            <td className="py-3 text-center">
                              <span className="badge bg-white  text-info bg-opacity-20  px-3 py-2 rounded-pill">
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
                  </Table>
                </Col>
              </Row>

              {/* Pagination Controls */}
              {dataTableShow.length > 0 && (
                <Row className="mt-3">
                  <Col className="d-flex justify-content-between align-items-center">
                    <div className="text-muted small">
                      {t('TXT_SHOWING_OPERATION_LOGS', { 
                        count: paginatedData.length, 
                        total: dataTableShow.length 
                      }) || `Showing ${paginatedData.length} of ${dataTableShow.length} records`}
                    </div>
                    <div className="d-flex align-items-center">
                      {/* Options limit */}
                      <select 
                        className="form-select form-select-sm d-inline-block w-auto me-3" 
                        value={limit} 
                        onChange={(e) => {
                          const newLimit = parseInt(e.target.value, 10);
                          setLimit(newLimit);
                          setPage(1); // Reset to first page when limit changes
                        }}
                      >
                        {optionsLimit.map((opt) => (
                          <option key={opt} value={opt}>{opt}</option>
                        ))}
                      </select>

                      {/* Previous button */}
                      <button 
                        className=" st-btn-material-outline me-2" 
                        disabled={page <= 1 || isLoading} 
                        onClick={() => {
                          if (page > 1) {
                            setPage(page - 1);
                          }
                        }}
                      >
                        <i className="mdi mdi-chevron-left"></i>
                        {t('BTN_PREVIOUS') || 'Previous'}
                      </button>

                      {/* List buttons of page */}
                      {listPages.map((p, index) => (
                        <button
                          key={index}
                          className={`btn me-1 ${p === page ? 'st-btn-material' : 'st-btn-material-outline'}`}
                          disabled={p === '...' || p === page || isLoading}
                          onClick={() => {
                            if (p !== '...' && p !== page) {
                              setPage(p);
                            }
                          }}
                        >
                          {p}
                        </button>
                      ))}

                      {/* Next button */}
                      <button 
                        className=" st-btn-material-outline" 
                        disabled={!isHaveMore || isLoading} 
                        onClick={() => {
                          if (isHaveMore) {
                            const nextPage = page + 1;
                            setPage(nextPage);
                          }
                        }}
                      >
                        <i className="mdi mdi-chevron-right"></i>
                        {t('BTN_NEXT_PAGE') || 'Next'}
                      </button>
                    </div>
                  </Col>
                </Row>
              )}
            </div>
          </Container>
        </div>
      </Container>

    </>
  );
};

export default LLMUsageAdminConsolePage;
