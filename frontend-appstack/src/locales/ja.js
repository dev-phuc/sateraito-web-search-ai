const JAPANESE_TRANSLATIONS = {
  translation: {
    TXT_COMPANY_NAME: "サテライト",
    TXT_APP_NAME: "サテライトウェブ検索AI",
    TXT_APP_DESCRIPTION: "AIを活用したウェブ検索体験を提供します",
    TXT_LOGIN_WITH_GOOGLE: "Googleでログイン",

    // =================== Messages from server ===================
    // Client websites
    internal_server_error: "内部サーバーエラー",
    id_is_required: "IDは必須です",
    domain_is_required: "ドメインは必須です",
    domain_already_exists: "ドメインは既に存在します",
    page_url_is_required: "ページURLは必須です",
    client_website_not_found: "クライアントウェブサイトが見つかりません",
    box_search_invalid_config: "ボックス検索の設定が無効です",
    // =================== End messages from server ===================

    // Common
    TXT_LOADING: "読み込み中",
    TXT_REFRESHING: "更新中...",
    TXT_REFRESH: "更新",
    TXT_RELOAD: "再読み込み",
    TXT_TOTAL_SELECTED: "選択済み",
    TXT_SELECT_ALL: "すべて選択",

    // Buttons
    BTN_CREATE: "作成",
    BTN_UPDATE: "更新",
    BTN_EDIT: "編集",
    BTN_DELETE: "削除",
    BTN_CANCEL: "キャンセル",
    BTN_YES: "はい",
    BTN_NO: "いいえ",

    // Status
    LABEL_STATUS: "ステータス",
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

    // SettingsTheme.jsx
    LAYOUT_BUILDER_LABEL: "レイアウトビルダー",
    LAYOUT_BUILDER_DES: "検索エンジンの外観をウェブサイトのデザインに合わせてカスタマイズします。",
    BGCOLOR_SCHEME_LABEL: "背景色スキーム",
    COLOR_SCHEME_LABEL: "カラースキーム",
    MENU_POSITION_LABEL: "メニュー位置",
    MENU_BEHAVIOR_LABEL: "メニュー動作",
    LAYOUT_LABEL: "レイアウト",

    // HeaderApp.jsx
    TXT_LOGOUT: "ログアウト",

    // Dashboard
    PAGE_TITLE_DASHBOARD_MANAGER: "ダッシュボード",

    // ClientWebsites
    PAGE_TITLE_CLIENT_WEBSITES: "クライアントウェブサイト",
    TITLE_CLIENT_WEBSITES_MANAGEMENT: "クライアントウェブサイト管理",
    BTN_ADD_DOMAIN: "ドメイン追加",
    TITLE_ADD_DOMAIN: "ドメイン追加",
    CONFIRM_DELETE_CLIENT_WEBSITE: "このクライアントウェブサイトを削除してもよろしいですか？",
    TITLE_CONFIRM_DELETE_CLIENT_WEBSITE: "クライアントウェブサイト削除",
    TXT_DELETE_CLIENT_WEBSITES_SUCCESS: "クライアントウェブサイトが正常に削除されました！",
    TXT_ERROR_DELETE_CLIENT_WEBSITES: "クライアントウェブサイトの削除に失敗しました。もう一度お試しください。",
    TXT_CREATE_CLIENT_WEBSITES_SUCCESS: "クライアントウェブサイトが正常に作成されました！",
    TXT_ERROR_CREATE_CLIENT_WEBSITES: "クライアントウェブサイトの作成に失敗しました。もう一度お試しください。",
    TXT_UPDATE_CLIENT_WEBSITES_SUCCESS: "クライアントウェブサイトが正常に更新されました！",
    TXT_ERROR_UPDATE_CLIENT_WEBSITES: "クライアントウェブサイトの更新に失敗しました。もう一度お試しください。",
    TXT_FETCH_CLIENT_WEBSITES_ERROR: "クライアントウェブサイトの取得に失敗しました。もう一度お試しください。",
    TXT_SELECT_AT_LEAST_ONE_ITEM: "少なくとも1つの項目を選択してください。",
    MSG_PLEASE_ADD_FIRST_CLIENT_WEBSITE: "最初のクライアントウェブサイトを追加してください。",
    MSG_DATA_CLIENT_WEBSITES_LOADING: "クライアントウェブサイトのデータを読み込み中...",
    NO_CLIENT_WEBSITES_FOUND: "クライアントウェブサイトが見つかりません。",
    // Form labels and placeholders
    LABEL_DOMAIN: "ドメイン",
    PLACEHOLDER_CLIENT_WEBSITES_DOMAIN: "ドメインを入力（例：example.com）",
    LABEL_FAVICON_URL: "ファビコンURL",
    PLACEHOLDER_CLIENT_WEBSITES_FAVICON_URL: "ファビコンURLを入力（例：https://example.com/favicon.ico）",
    LABEL_SITE_NAME: "サイト名",
    PLACEHOLDER_CLIENT_WEBSITES_SITE_NAME: "サイト名を入力",
    LABEL_DESCRIPTION: "説明",
    PLACEHOLDER_CLIENT_WEBSITES_DESCRIPTION: "説明を入力",
    LABEL_AI_ENABLED: "AI有効",
    // Error and warning messages
    MSG_ERROR_DOMAIN_REQUIRED: "ドメインは必須です！",
    MSG_ERROR_STATUS_REQUIRED: "ステータスは必須です！",
    MSG_ERROR_DOMAIN_INVALID: "ドメイン形式が無効です（例：example.com）",
    MSG_WARNING_FETCH_PAGE_INFO: "警告：ページ情報の取得に失敗しました。ドメインが到達不能の可能性があります。ドメインが正しい場合は、詳細を手動で入力してください。",
    // Table column names
    NAME_COL_WEBSITE_NAME: "ウェブサイト名",
    NAME_COL_WEBSITE_DESCRIPTION: "説明",
    NAME_COL_WEBSITE_URL: "ウェブサイトURL",
    NAME_COL_WEBSITE_AI_ENABLED: "AI有効",
    NAME_COL_STATUS: "ステータス",
    NAME_COL_CREATED_DATE: "作成日",
    NAME_COL_UPDATED_DATE: "更新日",
    NAME_COL_ACTIONS: "操作",

    // ClientWebsites
    PAGE_TITLE_BOX_SEARCH_CONFIG: "ボックス検索設定",
    TXT_ERROR_UPDATE_BOX_SEARCH_CONFIG: "ボックス検索設定の更新に失敗しました。もう一度お試しください。",
    TXT_UPDATE_BOX_SEARCH_CONFIG_SUCCESS: "ボックス検索設定が正常に更新されました！",
    LABEL_SEARCH_BOX: "検索ボックス",
    LABEL_TYPE: "タイプ",
    LABEL_BOX: "ボックス",
    LABEL_FULLSCREEN: "全画面",
    LABEL_FULLSCREEN_BLUR: "全画面ぼかし",
    LABEL_OPTIONS: "オプション",
    LABEL_BACKGROUND_COLOR: "背景色",
    LABEL_SHADOW: "シャドウ",
    LABEL_BORDER_RADIUS: "角丸",
    LABEL_FONT_SIZE: "フォントサイズ",
    LABEL_PADDING: "パディング",
    LABEL_SEARCH_BUTTON: "検索ボタン",
    LABEL_ICON: "アイコン",
    LABEL_COLOR: "色",
    LABEL_BUTTON_BORDER_RADIUS: "ボタン角丸",
    LABEL_BUTTON_BACKGROUND_COLOR: "ボタン背景色",
    LABEL_THEME: "テーマ",
    LABEL_FONT: "フォント",
    BTN_SUBMIT: "送信",
    BTN_CANCEL: "キャンセル",
    BTN_RESET: "リセット",
    BTN_RESET_TO_DEFAULTS: "デフォルトにリセット",
    TXT_LOADING: "読み込み中...",
    TXT_CHOOSE_SEARCH_UI: "検索UIの表示方法を選択してください。",
    TXT_PICK_BACKGROUND_COLOR: "検索ボックスの背景色を選択してください。",
    TXT_ENABLE_SHADOW: "ボックスにシャドウを追加します。",
    TXT_CORNER_RADIUS: "角丸のピクセル数。",
    TXT_ADJUST_FONT_SIZE: "フォントサイズを調整します。",
    TXT_INNER_SPACING: "検索ボックス内の余白。",
    TXT_ICON_PLACEHOLDER: "例：search、magnifier、またはSVGクラス",
    TXT_ICON_DESC: "Material Iconsなどのアイコンクラス名やURL。",
    TXT_BUTTON_CORNER_RADIUS: "ボタンの角丸ピクセル数。",
    TXT_FONT_PLACEHOLDER: "例：Inter、Arial、system-ui",
    TXT_FONT_DESC: "カンマ区切りのフォントファミリーのフォールバックリスト。",
    TXT_FORM_SUBMIT_CONDITION: "変更があり、バリデーションが通った場合のみフォームが送信されます。",
    LABEL_PREVIEW: "ライブプレビュー",
    TXT_PREVIEW_DESC: "検索ボックスの外観と操作感を確認できます",
    PLACEHOLDER_SEARCH: "何でも検索...",
    LABEL_SHOW_BOX_SEARCH: "検索ボックスを表示",
    LABEL_SHOW_BACKGROUND: "背景を表示",
  }
};

export default JAPANESE_TRANSLATIONS;
