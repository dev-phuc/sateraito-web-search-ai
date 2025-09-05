const VIETNAMESE_TRANSLATIONS = {
  translation: {
    TXT_COMPANY_NAME: "Sateraito",
    TXT_APP_NAME: "Sateraito AI Search",
    TXT_APP_DESCRIPTION: "Công cụ tìm kiếm AI cho trang web của bạn",
    TXT_LOGIN_WITH_GOOGLE: "Đăng nhập với Google",

    // =================== Messages from server ===================
    // Client websites
    internal_server_error: "Lỗi máy chủ nội bộ",
    id_is_required: "ID là bắt buộc",
    domain_is_required: "Tên miền là bắt buộc",
    domain_already_exists: "Tên miền đã tồn tại",
    page_url_is_required: "URL trang là bắt buộc",
    client_website_not_found: "Không tìm thấy trang web khách hàng",
    // =================== End messages from server ===================

    // Common
    TXT_LOADING: "Đang tải",
    TXT_REFRESHING: "Đang làm mới...",
    TXT_REFRESH: "Làm mới",
    TXT_RELOAD: "Tải lại",
    TXT_TOTAL_SELECTED: "đã chọn",
    TXT_SELECT_ALL: "Chọn tất cả",

    // Buttons
    BTN_CREATE: "Tạo mới",
    BTN_UPDATE: "Cập nhật",
    BTN_EDIT: "Chỉnh sửa",
    BTN_DELETE: "Xóa",
    BTN_CANCEL: "Hủy",
    BTN_YES: "Có",
    BTN_NO: "Không",

    // Status
    LABEL_STATUS: "Trạng thái",
    STATUS_ACTIVE: "Hoạt động",
    STATUS_DISABLED: "Đã vô hiệu hóa",
    STATUS_OVER_QUOTA: "Vượt hạn mức",
    LABEL_CREATED_DATE: "Ngày tạo",
    LABEL_UPDATED_DATE: "Ngày cập nhật",

    // SiderApp.jsx
    TXT_DASHBOARD: "Bảng điều khiển",
    TXT_DOMAINS_MANAGEMENT: "Quản lý tên miền",
    TXT_DESIGN_SEARCH_BOX: "Thiết kế hộp tìm kiếm",
    TXT_ENCODER_HTML_JS: "Mã hóa HTML/JS",
    TXT_DESIGN_BANNER_KEYWORDS: "Thiết kế Banner/Từ khóa",
    TXT_AI_CONFIGURATION: "Cấu hình AI",
    TXT_OPERATIONS_LOGS: "Nhật ký hoạt động",
    TXT_USAGE_STATISTICS: "Thống kê sử dụng",

    // SettingsTheme.jsx
    LAYOUT_BUILDER_LABEL: "Trình tạo bố cục",
    LAYOUT_BUILDER_DES: "Tùy chỉnh giao diện công cụ tìm kiếm để phù hợp với thiết kế trang web của bạn.",
    BGCOLOR_SCHEME_LABEL: "Màu nền",
    COLOR_SCHEME_LABEL: "Bảng màu",
    MENU_POSITION_LABEL: "Vị trí menu",
    MENU_BEHAVIOR_LABEL: "Hành vi menu",
    LAYOUT_LABEL: "Bố cục",

    // HeaderApp.jsx
    TXT_LOGOUT: "Đăng xuất",

    // Dashboard
    PAGE_TITLE_DASHBOARD_MANAGER: "Bảng điều khiển",

    // ClientWebsites
    PAGE_TITLE_CLIENT_WEBSITES: "Trang web khách hàng",
    TITLE_CLIENT_WEBSITES_MANAGEMENT: "Quản lý trang web khách hàng",
    BTN_ADD_DOMAIN: "Thêm tên miền",
    TITLE_ADD_DOMAIN: "Thêm tên miền",
    CONFIRM_DELETE_CLIENT_WEBSITE: "Bạn có chắc muốn xóa trang web khách hàng này không?",
    TITLE_CONFIRM_DELETE_CLIENT_WEBSITE: "Xóa trang web khách hàng",
    TXT_DELETE_CLIENT_WEBSITES_SUCCESS: "Xóa trang web khách hàng thành công!",
    TXT_ERROR_DELETE_CLIENT_WEBSITES: "Xóa trang web khách hàng thất bại. Vui lòng thử lại.",
    TXT_CREATE_CLIENT_WEBSITES_SUCCESS: "Tạo trang web khách hàng thành công!",
    TXT_ERROR_CREATE_CLIENT_WEBSITES: "Tạo trang web khách hàng thất bại. Vui lòng thử lại.",
    TXT_UPDATE_CLIENT_WEBSITES_SUCCESS: "Cập nhật trang web khách hàng thành công!",
    TXT_ERROR_UPDATE_CLIENT_WEBSITES: "Cập nhật trang web khách hàng thất bại. Vui lòng thử lại.",
    TXT_FETCH_CLIENT_WEBSITES_ERROR: "Lấy dữ liệu trang web khách hàng thất bại. Vui lòng thử lại.",
    TXT_SELECT_AT_LEAST_ONE_ITEM: "Vui lòng chọn ít nhất một mục.",
    MSG_PLEASE_ADD_FIRST_CLIENT_WEBSITE: "Vui lòng thêm trang web khách hàng đầu tiên của bạn.",
    MSG_DATA_CLIENT_WEBSITES_LOADING: "Đang tải dữ liệu trang web khách hàng...",
    NO_CLIENT_WEBSITES_FOUND: "Không tìm thấy trang web khách hàng nào.",
    // Form labels and placeholders
    LABEL_DOMAIN: "Tên miền",
    PLACEHOLDER_CLIENT_WEBSITES_DOMAIN: "Nhập tên miền (ví dụ: example.com)",
    LABEL_FAVICON_URL: "URL Favicon",
    PLACEHOLDER_CLIENT_WEBSITES_FAVICON_URL: "Nhập URL favicon (ví dụ: https://example.com/favicon.ico)",
    LABEL_SITE_NAME: "Tên trang web",
    PLACEHOLDER_CLIENT_WEBSITES_SITE_NAME: "Nhập tên trang web",
    LABEL_DESCRIPTION: "Mô tả",
    PLACEHOLDER_CLIENT_WEBSITES_DESCRIPTION: "Nhập mô tả",
    LABEL_AI_ENABLED: "Kích hoạt AI",
    // Error and warning messages
    MSG_ERROR_DOMAIN_REQUIRED: "Tên miền là bắt buộc!",
    MSG_ERROR_STATUS_REQUIRED: "Trạng thái là bắt buộc!",
    MSG_ERROR_DOMAIN_INVALID: "Định dạng tên miền không hợp lệ (ví dụ: example.com)",
    MSG_WARNING_FETCH_PAGE_INFO: "Cảnh báo: Không thể lấy thông tin trang. Tên miền có thể không truy cập được, nếu bạn chắc chắn tên miền đúng, vui lòng điền thông tin thủ công.",
    // Table column names
    NAME_COL_WEBSITE_NAME: "Tên trang web",
    NAME_COL_WEBSITE_DESCRIPTION: "Mô tả",
    NAME_COL_WEBSITE_URL: "URL trang web",
    NAME_COL_WEBSITE_AI_ENABLED: "Kích hoạt AI",
    NAME_COL_STATUS: "Trạng thái",
    NAME_COL_CREATED_DATE: "Ngày tạo",
    NAME_COL_UPDATED_DATE: "Ngày cập nhật",
    NAME_COL_ACTIONS: "Thao tác",
  }
};

export default VIETNAMESE_TRANSLATIONS;