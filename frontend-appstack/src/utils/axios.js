import axios from "axios";

const axiosInstance = axios.create({});

axiosInstance.interceptors.request.use(
  (config) => {
    // Do something before request is sent
    return config;
  },
  (error) => {
    // Do something with request error
    return Promise.reject(error);
  }
);

axiosInstance.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    if (error.response?.status === 401 || error.response?.status === 403) {
      console.log("ERROR_TIMEOUT");
      setTimeout(function () {
        window.location.reload();
      }, 2000);
    } else {
      // const errMessage = error.response?.data || error?.response || error;
      // return Promise.reject(errMessage);
      return Promise.reject(
        (error.response && error.response.data) || "Something went wrong"
      );
    }
  }
);

export default axiosInstance;
