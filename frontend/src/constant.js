export const BASE_URL = import.meta.env.VITE_VERCEL_BASE_URL;
export const SERVER_URL = import.meta.env.VITE_VERCEL_SERVER_URL;

export const LANGUAGE_SUPPORTED = ['en', 'ja', 'vi'];

export const DATETIME_FORMAT = "DD/MM/YYYY HH:mm:ss";
export const DATE_FORMAT = "DD/MM/YYYY";
export const TIME_FORMAT = "HH:mm:ss";

export const STATUS_CLIENT_WEBSITES_ACTIVE = 'active'
export const STATUS_CLIENT_WEBSITES_DISABLED = 'disabled'
export const STATUS_CLIENT_WEBSITES_OVER_QUOTA = 'over_quota'
export const STATUS_CLIENT_WEBSITES_LIST = [STATUS_CLIENT_WEBSITES_ACTIVE, STATUS_CLIENT_WEBSITES_DISABLED, STATUS_CLIENT_WEBSITES_OVER_QUOTA]