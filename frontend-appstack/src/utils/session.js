// import jwtDecode from "jwt-decode";
// import { verify, sign } from "jsonwebtoken";
import axios from "@/utils/axios";

const getSession = () => {
  return localStorage.getItem("sessionLoggedIn");
};

const setSession = (accessToken) => {
  if (accessToken) {
    localStorage.setItem("sessionLoggedIn", accessToken);
    // axios.defaults.headers.common.Authorization = `Bearer ${accessToken}`;
    // This function below will handle when token is expired
    // const { exp } = jwtDecode(accessToken);
    // handleTokenExpired(exp);
  } else {
    localStorage.removeItem("sessionLoggedIn");
    // delete axios.defaults.headers.common.Authorization;
  }
};

export { getSession, setSession };
