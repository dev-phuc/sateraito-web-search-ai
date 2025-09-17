import usFlag from "@/assets/img/flags/us.png";
import jpFlag from "@/assets/img/flags/jp.png";
import vnFlag from "@/assets/img/flags/vn.png";
import frFlag from "@/assets/img/flags/fr.png";
import deFlag from "@/assets/img/flags/de.png";
import nlFlag from "@/assets/img/flags/nl.png";
import krFlag from "@/assets/img/flags/kr.png";
import cnFlag from "@/assets/img/flags/cn.png";
import thFlag from "@/assets/img/flags/th.png";

export const SERVER_URL = import.meta.env.VITE_BASE_URL || "http://localhost:8000";
export const SECRET_KEY_CRYPTO_JS = import.meta.env.VITE_SECRET_KEY_CRYPTO_JS;

export const NAME_PATH_FIREBASE_REALTIME_DATABASE = "web-search-ai";

export const SIDEBAR_POSITION = {
  LEFT: "left",
  RIGHT: "right",
};

export const SIDEBAR_BEHAVIOR = {
  STICKY: "sticky",
  FIXED: "fixed",
  COMPACT: "compact",
};

export const LAYOUT = {
  FLUID: "fluid",
  BOXED: "boxed",
  MATERIAL: "material",
};

export const THEME = {
  DEFAULT: "default",
  SKIN_COLOR_DEFAULT: "#673ab7",
  COLORED: "colored",
  DARK: "dark",
  LIGHT: "light",
};

export const THEME_PALETTE_LIGHT = {
  primary: "#3B82EC",
  "primary-dark": "#1659c7",
  "primary-light": "#84aef2",
  secondary: "#495057",
  success: "#4BBF73",
  info: "#1F9BCF",
  warning: "#f0ad4e",
  danger: "#d9534f",
  white: "#fff",
  "gray-100": "#f4f7f9",
  "gray-200": "#e2e8ee",
  "gray-300": "#dee6ed",
  "gray-400": "#ced4da",
  "gray-500": "#adb5bd",
  "gray-600": "#6c757d",
  "gray-700": "#495057",
  "gray-800": "#020202",
  "gray-900": "#212529",
  black: "#000",
};

export const THEME_PALETTE_DARK = {
  ...THEME_PALETTE_LIGHT,
  "primary-dark": "#84aef2",
  "primary-light": "#1659c7",
  white: "#293042",
  "gray-100": "#3e4555",
  "gray-200": "#545968",
  "gray-300": "#696e7b",
  "gray-400": "#7f838e",
  "gray-500": "#9498a1",
  "gray-600": "#a9acb3",
  "gray-700": "#bfc1c6",
  "gray-800": "#d4d6d9",
  "gray-900": "#eaeaec",
  black: "#fff",
};

export const NOTIFY_CONFIG = {
  TYPE: {
    DEFAULT: "default",
    SUCCESS: "success",
    WARNING: "warning",
    DANGER: "danger",
  },
  DURATION: 2500,
  RIPPLE: true,
  DISMISSIBLE: false,
  POSITION: {
    TOP: "top",
    LEFT: "left",
    RIGHT: "right",
    BOTTOM: "bottom",
    CENTER: "center",
  },
};

export const DEFAULT_SETTING_TEXT_COLOR = "#ffffff";
export const DEFAULT_SETTING_BACKGROUND_COLOR = "#2196f3";

export const KEY_ROLE_ADMIN = "admin";
export const KEY_ROLE_CREATOR = "creator";
export const KEY_ROLE_USER = "user";

export const KEY_CHARACTER_DEFAULT = "character_default";

export const KEY_FEEDBACK_GOOD = "good";
export const KEY_FEEDBACK_BAD = "bad";

export const KEY_STATUS_BOOK_PUBLIC = "BOOK_PUBLIC";
export const KEY_STATUS_BOOK_SHARE = "BOOK_SHARE";
export const KEY_STATUS_BOOK_PRIVATE = "BOOK_PRIVATE";

export const KEY_TYPE_BOOK_SHARE = "book";
export const KEY_TYPE_STORY_SHARE = "story";
export const KEY_TYPE_CHAPTER_SHARE = "chapter";

export const KEY_REQUEST_SUCCESS = "ok";

export const KEY_STATUS_COMPLETE = "complete";
export const KEY_STATUS_PROCESSING = "processing";
export const KEY_STATUS_ERROR = "error";

export const KEY_SIGN_IN_WITH_GOOGLE = 'SIGN_IN_WITH_GOOGLE'
export const KEY_SIGN_IN_WITH_FACEBOOK = 'SIGN_IN_WITH_FACEBOOK'
export const KEY_SIGN_IN_WITH_LINE = 'SIGN_IN_WITH_LINE'
export const KEY_SIGN_IN_WITH_TWITTER = 'SIGN_IN_WITH_TWITTER'
export const KEY_SIGN_IN_WITH_USERNAME_PASSWORD = 'SIGN_IN_WITH_USERNAME_PASSWORD'

export const MAX_REQUEST_RETRY = 5;
export const RETRY_DELAY = 1000;

export const LANGUAGE_OPTIONS = {
  en: {
    icon: usFlag,
    name: "English",
  },
  ja: {
    icon: jpFlag,
    name: "Japanese",
  },
  vi: {
    icon: vnFlag,
    name: "Vietnamese",
  },
  fr: {
    icon: frFlag,
    name: "French",
  },
  ko: {
    icon: krFlag,
    name: "Korea",
  },
  cn: {
    icon: cnFlag,
    name: "China",
  },
  th: {
    icon: thFlag,
    name: "Thailand",
  },
};

export const LANGUAGE_DEFAULT = 'ja';
export const LANGUAGE_SUPPORTED = ['en', 'ja', 'vi'];

export const DATETIME_FORMAT = "DD/MM/YYYY HH:mm:ss";
export const DATE_FORMAT = "DD/MM/YYYY";
export const TIME_FORMAT = "HH:mm:ss";

export const STATUS_CLIENT_WEBSITES_ACTIVE = 'active'
export const STATUS_CLIENT_WEBSITES_DISABLED = 'disabled'
export const STATUS_CLIENT_WEBSITES_OVER_QUOTA = 'over_quota'
export const STATUS_CLIENT_WEBSITES_LIST = [STATUS_CLIENT_WEBSITES_ACTIVE, STATUS_CLIENT_WEBSITES_DISABLED, STATUS_CLIENT_WEBSITES_OVER_QUOTA]

export const BOX_SEARCH_DESIGN_DEFAULT = {
	"search_box": {
		"type": "box", // box, fullscreen and fullscreen_blur
		"options": {
			"background_color": "#ffffff",
			"shadow": true,
			"border_radius": 8,
			"font-size": 14,
			"padding": 5,
		}
	},
	"search_button": {
		"icon": "mdi-magnify",
		"color": "#1976d2",
		"background_color": "#e3f2fd",
		"border_radius": 8,
	},
	"theme": {
		"color": "#1976d2",
		"font": "Arial, sans-serif"
	}
}

export const LLM_CONFIGURATION_DEFAULT = {
	"model_name": 'sonar',
	"system_prompt": 'You are a helpful assistant.',
  'max_characters': 1000,
	"response_length_level": 'medium', // short, medium, long
}

export const BOX_SEARCH_TO_HTML_TEMPLATE = `<link rel="stylesheet" href="SERVER_URL/static/@mdi/font/css/materialdesignicons.min.css">
<link rel="stylesheet" href="SERVER_URL/static/box-search-ai/style.css">

<div id="sateraito-ai-root"></div>

<script>
  window.SateraitoAIAsyncInit = function () {
    SateraitoAI.init({
      tenant: 'TENANT',
      appId: 'APP_ID',
    });
  };
</script>
<script async defer src="SERVER_URL/static/sdk.js"></script>
`