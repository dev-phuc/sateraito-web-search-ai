const JAPANESE_TRANSLATIONS = {
  translation: {
    TXT_COMPANY_NAME: "サテライト",
    TXT_APP_NAME: "サテライトウェブ検索AI",
    TXT_APP_DESCRIPTION: "AIを活用したウェブ検索体験を提供します",
    TXT_LOGIN_WITH_GOOGLE: "Googleでログイン",

    // =================== サーバーからのメッセージ ===================
    // クライアントウェブサイト
    internal_server_error: "内部サーバーエラー",
    id_is_required: "IDは必須です",
    domain_is_required: "ドメインは必須です",
    domain_already_exists: "ドメインは既に存在します",
    page_url_is_required: "ページURLは必須です",
    client_website_not_found: "クライアントウェブサイトが見つかりません",
    // =================== サーバーからのメッセージ終了 ===================

    // 共通
    TXT_LOADING: "読み込み中",
    LABEL_STATUS: "ステータス",
    BTN_CREATE: "作成",
    BTN_UPDATE: "更新",
    BTN_EDIT: "編集",
    BTN_DELETE: "削除",
    BTN_CANCEL: "キャンセル",
    BTN_YES: "はい",
    BTN_NO: "いいえ",
    STATUS_ACTIVE: "有効",
    STATUS_DISABLED: "無効",
    STATUS_OVER_QUOTA: "上限超過",
    LABEL_CREATED_DATE: "作成日",
    LABEL_UPDATED_DATE: "更新日",

    // SiderApp.jsx
    TXT_DASHBOARD: "ダッシュボード",
    TXT_DOMAINS_MANAGEMENT: "ドメイン管理",
    TXT_DESIGN_SEARCH_BOX: "検索ボックスデザイン",
    TXT_ENCODER_HTML_JS: "エンコーダーHTML/JS",
    TXT_DESIGN_BANNER_KEYWORDS: "バナー/キーワードデザイン",
    TXT_AI_CONFIGURATION: "AI設定",
    TXT_OPERATIONS_LOGS: "操作ログ",
    TXT_USAGE_STATISTICS: "利用統計",

    // HeaderApp.jsx
    TXT_LOGOUT: "ログアウト",

    // ClientWebsites
    TITLE_CLIENT_WEBSITES_MANAGEMENT: "クライアントウェブサイト管理",
    BTN_ADD_DOMAIN: "ドメイン追加",
    TITLE_ADD_DOMAIN: "ドメイン追加",
    CONFIRM_DELETE_CLIENT_WEBSITE: "このクライアントウェブサイトを削除してもよろしいですか？",
    TXT_CREATE_CLIENT_WEBSITES_SUCCESS: "クライアントウェブサイトの作成に成功しました！",
    TXT_ERROR_CREATE_CLIENT_WEBSITES: "クライアントウェブサイトの作成に失敗しました。再度お試しください。",
    TXT_UPDATE_CLIENT_WEBSITES_SUCCESS: "クライアントウェブサイトの更新に成功しました！",
    TXT_ERROR_UPDATE_CLIENT_WEBSITES: "クライアントウェブサイトの更新に失敗しました。再度お試しください。",
    TXT_FETCH_CLIENT_WEBSITES_ERROR: "クライアントウェブサイトの取得に失敗しました。再度お試しください。",
    LABEL_DOMAIN: "ドメイン",
    PLACEHOLDER_CLIENT_WEBSITES_DOMAIN: "ドメインを入力（例：example.com）",
    MSG_ERROR_DOMAIN_REQUIRED: "ドメインは必須です！",
    LABEL_FAVICON_URL: "ファビコンURL",
    PLACEHOLDER_CLIENT_WEBSITES_FAVICON_URL: "ファビコンURLを入力（例：https://example.com/favicon.ico）",
    LABEL_SITE_NAME: "サイト名",
    PLACEHOLDER_CLIENT_WEBSITES_SITE_NAME: "サイト名を入力",
    LABEL_DESCRIPTION: "説明",
    PLACEHOLDER_CLIENT_WEBSITES_DESCRIPTION: "説明を入力",
    LABEL_AI_ENABLED: "AI有効",
    MSG_ERROR_STATUS_REQUIRED: "ステータスは必須です！",
    MSG_ERROR_DOMAIN_INVALID: "ドメイン形式が無効です（例：example.com）",
    MSG_WARNING_FETCH_PAGE_INFO: "警告：ページ情報の取得に失敗しました。ドメインにアクセスできない可能性があります。正しいドメインであれば、手動で詳細を入力してください。",
  }
};

export default JAPANESE_TRANSLATIONS;
