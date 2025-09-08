const ENGLISH_TRANSLATIONS = {
  translation: {
    TXT_COMPANY_NAME: "Sateraito",
    TXT_APP_NAME: "Sateraito AI Search",
    TXT_APP_DESCRIPTION: "AI-powered search engine for your website",
    TXT_LOGIN_WITH_GOOGLE: "Sign in with Google",

    // =================== Messages from server ===================
    // Client websites
    internal_server_error: "Internal server error",
    id_is_required: "ID is required",
    domain_is_required: "Domain is required",
    domain_already_exists: "Domain already exists",
    page_url_is_required: "Page URL is required",
    client_website_not_found: "Client website not found",
    box_search_invalid_config: "Box search config is invalid",
    // =================== End messages from server ===================

    // Common
    TXT_LOADING: "Loading",
    TXT_REFRESHING: "Refreshing...",
    TXT_REFRESH: "Refresh",
    TXT_RELOAD: "Reload",
    TXT_TOTAL_SELECTED: "selected",
    TXT_SELECT_ALL: "Select All",

    // Buttons
    BTN_CREATE: "Create",
    BTN_UPDATE: "Update",
    BTN_EDIT: "Edit",
    BTN_DELETE: "Delete",
    BTN_CANCEL: "Cancel",
    BTN_YES: "Yes",
    BTN_NO: "No",

    // Status
    LABEL_STATUS: "Status",
    STATUS_ACTIVE: "Active",
    STATUS_DISABLED: "Disabled",
    STATUS_OVER_QUOTA: "Over Quota",
    LABEL_CREATED_DATE: "Created Date",
    LABEL_UPDATED_DATE: "Updated Date",

    // SiderApp.jsx
    TXT_DASHBOARD: "Dashboard",
    TXT_DOMAINS_MANAGEMENT: "Domains Management",
    TXT_DESIGN_SEARCH_BOX: "Design Search Box",
    TXT_ENCODER_HTML_JS: "Encoder HTML/JS",
    TXT_DESIGN_BANNER_KEYWORDS: "Design Banner/Keywords",
    TXT_AI_CONFIGURATION: "AI Configuration",
    TXT_OPERATIONS_LOGS: "Operations Logs",
    TXT_USAGE_STATISTICS: "Usage Statistics",

    // SettingsTheme.jsx
    LAYOUT_BUILDER_LABEL: "Layout Builder",
    LAYOUT_BUILDER_DES: "Customize the appearance of your search engine to match your website's design.",
    BGCOLOR_SCHEME_LABEL: "Background Color Scheme",
    COLOR_SCHEME_LABEL: "Color Scheme",
    MENU_POSITION_LABEL: "Menu Position",
    MENU_BEHAVIOR_LABEL: "Menu Behavior",
    LAYOUT_LABEL: "Layout",

    // HeaderApp.jsx
    TXT_LOGOUT: "Logout",

    // Login
    PAGE_TITLE_LOGIN: "Sign In",
    TXT_LOGIN_FAILED_PLEASE_TRY_AGAIN: "Login failed, please try again.",

    // Dashboard
    PAGE_TITLE_DASHBOARD_MANAGER: "Dashboard",

    // ClientWebsites
    PAGE_TITLE_CLIENT_WEBSITES: "Client Websites",
    TITLE_CLIENT_WEBSITES_MANAGEMENT: "Client Websites Management",
    BTN_ADD_DOMAIN: "Add Domain",
    TITLE_ADD_DOMAIN: "Add Domain",
    CONFIRM_DELETE_CLIENT_WEBSITE: "Are you sure you want to delete this client website?",
    TITLE_CONFIRM_DELETE_CLIENT_WEBSITE: "Delete Client Website",
    TXT_DELETE_CLIENT_WEBSITES_SUCCESS: "Client website deleted successfully!",
    TXT_ERROR_DELETE_CLIENT_WEBSITES: "Failed to delete client website. Please try again.",
    TXT_CREATE_CLIENT_WEBSITES_SUCCESS: "Client website created successfully!",
    TXT_ERROR_CREATE_CLIENT_WEBSITES: "Failed to create client website. Please try again.",
    TXT_UPDATE_CLIENT_WEBSITES_SUCCESS: "Client website updated successfully!",
    TXT_ERROR_UPDATE_CLIENT_WEBSITES: "Failed to update client website. Please try again.",
    TXT_FETCH_CLIENT_WEBSITES_ERROR: "Failed to fetch client websites. Please try again.",
    TXT_SELECT_AT_LEAST_ONE_ITEM: "Please select at least one item.",
    MSG_PLEASE_ADD_FIRST_CLIENT_WEBSITE: "Please add your first client website.",
    MSG_DATA_CLIENT_WEBSITES_LOADING: "Client websites data is loading...",
    NO_CLIENT_WEBSITES_FOUND: "No client websites found.",
    // Form labels and placeholders
    LABEL_DOMAIN: "Domain",
    PLACEHOLDER_CLIENT_WEBSITES_DOMAIN: "Enter domain (e.g., example.com)",
    LABEL_FAVICON_URL: "Favicon URL",
    PLACEHOLDER_CLIENT_WEBSITES_FAVICON_URL: "Enter favicon URL (e.g., https://example.com/favicon.ico)",
    LABEL_SITE_NAME: "Site Name",
    PLACEHOLDER_CLIENT_WEBSITES_SITE_NAME: "Enter site name",
    LABEL_DESCRIPTION: "Description",
    PLACEHOLDER_CLIENT_WEBSITES_DESCRIPTION: "Enter description",
    LABEL_AI_ENABLED: "AI Enabled",
    // Error and warning messages
    MSG_ERROR_DOMAIN_REQUIRED: "Domain is required!",
    MSG_ERROR_STATUS_REQUIRED: "Status is required!",
    MSG_ERROR_DOMAIN_INVALID: "Domain format is invalid (e.g., example.com)",
    MSG_WARNING_FETCH_PAGE_INFO: "Warning: Failed to fetch page info. The domain might be unreachable, if you are sure the domain is correct, please fill in the details manually.",
    // Table column names
    NAME_COL_WEBSITE_NAME: "Website Name",
    NAME_COL_WEBSITE_DESCRIPTION: "Description",
    NAME_COL_WEBSITE_URL: "Website URL",
    NAME_COL_WEBSITE_AI_ENABLED: "AI Enabled",
    NAME_COL_STATUS: "Status",
    NAME_COL_CREATED_DATE: "Created Date",
    NAME_COL_UPDATED_DATE: "Updated Date",
    NAME_COL_ACTIONS: "Actions",

    // ClientWebsites
    PAGE_TITLE_BOX_SEARCH_CONFIG: "Box Search Config",
    TXT_ERROR_UPDATE_BOX_SEARCH_CONFIG: "Failed to update box search config. Please try again.",
    TXT_UPDATE_BOX_SEARCH_CONFIG_SUCCESS: "Box search config updated successfully!",
    TXT_ERROR_UPDATE_BOX_SEARCH_CONFIG: "Failed to update box search config. Please try again.",
    LABEL_SEARCH_BOX: "Search Box",
    LABEL_TYPE: "Type",
    LABEL_BOX: "Box",
    LABEL_FULLSCREEN: "Fullscreen",
    LABEL_FULLSCREEN_BLUR: "Fullscreen Blur",
    LABEL_OPTIONS: "Options",
    LABEL_BACKGROUND_COLOR: "Background Color",
    LABEL_SHADOW: "Shadow",
    LABEL_BORDER_RADIUS: "Border Radius",
    LABEL_FONT_SIZE: "Font Size",
    LABEL_PADDING: "Padding",
    LABEL_SEARCH_BUTTON: "Search Button",
    LABEL_ICON: "Icon",
    LABEL_COLOR: "Color",
    LABEL_BUTTON_BORDER_RADIUS: "Button Border Radius",
    LABEL_BUTTON_BACKGROUND_COLOR: "Button Background Color",
    LABEL_THEME: "Theme",
    LABEL_FONT: "Font",
    BTN_SUBMIT: "Submit",
    BTN_CANCEL: "Cancel",
    BTN_RESET: "Reset",
    BTN_RESET_TO_DEFAULTS: "Reset to defaults",
    TXT_LOADING: "Loading...",
    TXT_CHOOSE_SEARCH_UI: "Choose how the search UI should appear to users.",
    TXT_PICK_BACKGROUND_COLOR: "Pick a background color for the search box.",
    TXT_ENABLE_SHADOW: "Enable a subtle shadow to lift the box visually.",
    TXT_CORNER_RADIUS: "Corner radius in pixels.",
    TXT_ADJUST_FONT_SIZE: "Adjust the input font size.",
    TXT_INNER_SPACING: "Inner spacing inside the search box.",
    TXT_ICON_PLACEHOLDER: "e.g. search, magnifier or SVG class",
    TXT_ICON_DESC: "Class name icon libraries like Material Icons or url.",
    TXT_BUTTON_CORNER_RADIUS: "Button corner radius in pixels.",
    TXT_FONT_PLACEHOLDER: "e.g. Inter, Arial, system-ui",
    TXT_FONT_DESC: "Comma-separated font family fallback list.",
    TXT_FORM_SUBMIT_CONDITION: "The form will only submit when there are changes and validation passes.",
    LABEL_PREVIEW: "Live Preview",
    TXT_PREVIEW_DESC: "See how your search box will look and feel",
    PLACEHOLDER_SEARCH: "Search anything...",
    LABEL_SHOW_BOX_SEARCH: "Show search box",
    LABEL_SHOW_BACKGROUND: "Show background",

    // Other translations can be added here
  }
};

export default ENGLISH_TRANSLATIONS;