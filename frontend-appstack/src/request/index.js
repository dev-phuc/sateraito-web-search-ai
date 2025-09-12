// The request module is used to handle API requests in the application.
import axios from 'axios';
import { getNewIdQuestion, convertPathRealTimeFirebaseDatabase } from '@/utils';
import { SERVER_URL } from "@/constants";

// Firebase real-time database
import { database } from '@/firebase';
import { ref, set, onValue } from "firebase/database";

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

export const get = (url, params = {}, headers = {}) => {
  return apiClient.get(url, { params, headers });
}

export const post = (url, data, headers = {}) => {
  if (headers['Content-Type'] === 'multipart/form-data') {
    return apiFormDataClient.post(url, data, { headers });
  }

  return apiClient.post(url, data, { headers });
}

export const put = (url, data, headers = {}) => {
  if (headers['Content-Type'] === 'multipart/form-data') {
    return apiFormDataClient.put(url, data, { headers });
  }
  return apiClient.put(url, data, { headers });
}

export const deleteReq = (url, params = {}) => {
  return apiClient.delete(url, { params });
}

export const postStream = async (url, data, headers = {}, onStream = null) => {
  /**
   * 
  // Use fetch
  const fullURL = `${SERVER_URL}${url}`;

  const fetch = window.fetch;
  const controller = new AbortController();
  const signal = controller.signal;

  const fetchOptions = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...headers
    },
    body: JSON.stringify(data),
    signal
  };

  const response = await fetch(fullURL, fetchOptions);
  if (!response.body) throw new Error("No body in response");

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  let dataResult = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let lines = buffer.split("\n\n");
    buffer = lines.pop();

    for (const eventText of lines) {
      const event = {};
      eventText.split("\n").forEach(line => {
        if (line.startsWith("id:")) event.id = line.slice(3);
        else if (line.startsWith("event:")) event.event = line.slice(6);
        else if (line.startsWith("data:")) {
          event.data = (event.data || "") + line.slice(5);
        }
      });

      let typeEvent = event.event || "message";
      let dataEvent = event.data || "";

      // ReplaceAll s_endline with \n
      event.data = dataEvent.replaceAll("s_endline", "\n");

      dataResult += dataEvent;

      if (onStream) {
        onStream(typeEvent.trim(), event);
      }
    }
  }

  return dataResult;
  */

  let request;
  const { tenant, app_id, query } = data;

  // Validate tenant and app_id
  if (!tenant) throw new Error("Tenant is required in data");
  if (!app_id) throw new Error("App ID is required in data");
  if (!query) throw new Error("Query is required in data");

  const uniqueId = getNewIdQuestion();
  url += (url.includes('?') ? '&' : '?') + `stream_id=${uniqueId}`;
  const pathStreamingRequest = convertPathRealTimeFirebaseDatabase(`/${tenant}/${app_id}/streaming-requests/${uniqueId}`);

  // Save initial question to Firebase real-time database
  set(ref(database, pathStreamingRequest), {
    id: uniqueId,
    tenant,
    app_id,
    question: query,
    created_at: Date.now(),
    status: 'started'
  });

  // Onchange data in Firebase real-time database
  if (onStream) {
    const streamRef = ref(database, pathStreamingRequest);
    // Listen for changes
    const unsubscribe = onValue(streamRef, (snapshot) => {
      const val = snapshot.val();
      if (val && val.answer) {
        onStream('message', { id: uniqueId, event: 'message', data: val.answer });
      }
      if (val && val.metadata) {
        onStream('metadata', { id: uniqueId, event: 'metadata', data: val.metadata });
      }
      if (val && val.status === 'completed') {
        onStream('done', { id: uniqueId, event: 'done', data: '' });
        unsubscribe(); // Stop listening after completion
      }
      if (val && val.status === 'error') {
        onStream('error', { id: uniqueId, event: 'error', data: val.error || 'Error occurred' });
        unsubscribe(); // Stop listening after error
      }
    });
  }

  // Additional headers
  headers['X-Stream-ID'] = uniqueId;
  headers['X-Stream-Path'] = pathStreamingRequest;
  headers['X-Tenant'] = tenant;
  headers['X-App-ID'] = app_id;

  // Use axios
  if (headers['Content-Type'] === 'multipart/form-data') {
    request = await apiFormDataClient.post(url, data, { headers });
  } else {
    request = await apiClient.post(url, data, { headers });
  }

  if (!request.data) throw new Error("No data in response");

  return request.data;
};

// Export apiClient for direct use in other modules
export { apiClient, apiFormDataClient };