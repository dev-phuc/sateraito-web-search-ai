// The request module is used to handle API requests in the application.
import axios from 'axios';

import { SERVER_URL } from "@/constant";
console.log(SERVER_URL);

const apiClient = axios.create({
  baseURL: SERVER_URL,
  withCredentials: true, // Include credentials for cross-origin requests
  headers: {
    'Content-Type': 'application/json',
  },
});

const apiFormDataClient = axios.create({
  baseURL: import.meta.env.VITE_VERCEL_SERVER_URL,
  withCredentials: true, // Include credentials for cross-origin requests
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

// Response interceptor for form data client (same as regular client)
apiFormDataClient.interceptors.response.use(
  response => {
    // Transform new backend response format to maintain compatibility
    if (response.data && typeof response.data === 'object' && 'success' in response.data) {
      if (response.data.success) {
        response.data = response.data.data;
      } else {
        const error = new Error(response.data.message || 'API Error');
        error.response = response;
        error.response.data = {
          message: response.data.message,
          error: response.data.message, // Also set error field for backward compatibility
          details: response.data.details
        };
        throw error;
      }
    }
    return response;
  },
  error => {
    // Same error handling as regular client
    if (error.response && error.response.status === 401) {
      console.error('Unauthorized access - redirecting to login');
      const requestURL = error.config.url;
      if (requestURL && requestURL.includes('/auth/login')) {
        console.error('Login request failed, but not redirecting to login page again.');
      } else {
        // window.location.href = '/dang-nhap';
      }
    } else {
      console.error('API request error:', {
        url: error.config?.url,
        method: error.config?.method,
        status: error.response?.status,
        message: error.response?.data?.message || error.message,
        data: error.response?.data
      });
    }
    return Promise.reject(error);
  }
);

// Request interceptor for debugging
apiClient.interceptors.request.use(
  config => {
    // console.log('API Request:', {
    //   method: config.method?.toUpperCase(),
    //   url: config.url,
    //   baseURL: config.baseURL,
    //   fullURL: `${config.baseURL}${config.url}`,
    //   params: config.params,
    //   data: config.data
    // });
    return config;
  },
  error => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Interceptor to handle request errors and transform new API response format
apiClient.interceptors.response.use(
  response => {
    // Transform new backend response format to maintain compatibility
    // New format: { success: true, message: "...", data: {...} }
    // Old expected format: direct data in response.data
    if (response.data && typeof response.data === 'object' && 'success' in response.data) {
      // If it's the new standardized response format
      if (response.data.success) {
        // For success responses, return the data directly to maintain compatibility
        response.data = response.data.data;
      } else {
        // For error responses, throw an error with the message
        const error = new Error(response.data.message || 'API Error');
        error.response = response;
        error.response.data = {
          message: response.data.message,
          error: response.data.message, // Also set error field for backward compatibility
          details: response.data.details
        };
        throw error;
      }
    }
    return response;
  },
  error => {
    if (error.response && error.response.status === 401) {
      // Handle unauthorized access, e.g., redirect to login
      console.error('Unauthorized access - redirecting to login');
      const requestURL = error.config.url;
      if (requestURL && requestURL.includes('/auth/login')) {
        // If the request is for login, do not redirect to login again
        console.error('Login request failed, but not redirecting to login page again.');
      } else {
        // window.location.href = '/dang-nhap';
      }
    } else {
      // Handle other errors with more detailed logging
      console.error('API request error:', {
        url: error.config?.url,
        method: error.config?.method,
        status: error.response?.status,
        message: error.response?.data?.message || error.message,
        data: error.response?.data
      });
    }
    return Promise.reject(error);
  }
);

export const get = (url, params = {}) => {
  return apiClient.get(url, { params });
}

export const post = (url, data, headers={}) => {
  if (headers['Content-Type'] === 'multipart/form-data') {
    return apiFormDataClient.post(url, data, { headers });
  }

  return apiClient.post(url, data, { headers });
}

export const put = (url, data, headers={}) => {
  if (headers['Content-Type'] === 'multipart/form-data') {
    return apiFormDataClient.put(url, data, { headers });
  }
  return apiClient.put(url, data, { headers });
}

export const deleteRequest = (url, params = {}) => {
  return apiClient.delete(url, { params });
} 

export const getApi = (url, params = {}) => {
  return apiClient.get(`api${url}`, { params });
}

export const postApi = (url, data, headers={}) => {
  if (headers['Content-Type'] === 'multipart/form-data') {
    return apiFormDataClient.post(`api${url}`, data, { headers });
  }

  return apiClient.post(`api${url}`, data, { headers });
}

export const putApi = (url, data, headers={}) => {
  if (headers['Content-Type'] === 'multipart/form-data') {
    return apiFormDataClient.put(`api${url}`, data, { headers });
  }
  return apiClient.put(`api${url}`, data, { headers });
}

export const patchApi = (url, data, headers={}) => {
  if (headers['Content-Type'] === 'multipart/form-data') {
    return apiFormDataClient.patch(`api${url}`, data, { headers });
  }
  return apiClient.patch(`api${url}`, data, { headers });
}

export const deleteApi = (url, params = {}) => {
  return apiClient.delete(`api${url}`, { params });
}

// Export apiClient for direct use in other modules
export { apiClient, apiFormDataClient };