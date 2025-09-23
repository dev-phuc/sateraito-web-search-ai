import { format } from "date-fns";
import CryptoJS from "crypto-js";

import { SECRET_KEY_CRYPTO_JS, NAME_PATH_FIREBASE_REALTIME_DATABASE } from "@/constants";

export const dateStringToTimestamp = (strDate) => {
  const dt = Date.parse(strDate);
  return dt / 1000;
};
export const stringDateToISOString = (strDate) => {
  let d = new Date();
  if (strDate) {
    d = new Date(strDate);
  }
  return d.toISOString();
};
export const formatDate = (strDate, strFormat = "yyyy/MM/dd HH:MM") => {
  if (strDate) {
    let d = strDate;
    if (typeof strDate === "string") {
      d = new Date(strDate);
    }
    return format(d, strFormat);
  }
  return "";
};

export const truncateText = (text, maxLength = 50) => {
  if (!text) return '-';
  return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text;
};

export const capitalize = (s) => {
  let firstChar = /\S/;
  return s.replace(firstChar, function (m) {
    return m.toUpperCase();
  });
};

export const Highlighter = ({ children, highlight }) => {
  if (!highlight) return children;
  const regexp = new RegExp(highlight, "g");
  const matches = children.match(regexp);
  console.log(matches, parts);
  var parts = children.split(new RegExp(`${highlight.replace()}`, "g"));

  for (var i = 0; i < parts.length; i++) {
    if (i !== parts.length - 1) {
      let match = matches[i];
      // While the next part is an empty string, merge the corresponding match with the current
      // match into a single <span/> to avoid consequent spans with nothing between them.
      while (parts[i + 1] === "") {
        match += matches[++i];
      }

      parts[i] = `${parts[i]} <span className="highlighted">${match}</span>`;
    }
  }
  return `<div className="highlighter">${parts}</div>`;
};

export const validateEmail = (emailStr) => {
  let mailformat = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
  if (emailStr.match(mailformat)) {
    return true;
  }
  return false;
};

export const validateDomainOrUrl = (domainOrUrl) => {
  let domainformat = /^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$/;
  let urlformat = /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([\/\w .-]*)*\/?$/;

  if (domainOrUrl.match(domainformat) || domainOrUrl.match(urlformat)) {
    return true;
  }
  return false;
};

export const parseTextSearchResultSnipet = (text) => {
  if (typeof text !== "string") {
    return "";
  }
  text = text.trim();
  let text_split = text.split(" ");
  if (text_split.length) {
    if (validateEmail(text_split[0])) {
      text_split.splice(0, 1);
    }
  }
  let result = text_split.join(" ");
  result = result.trim();
  return result;
};

export const htmlDecode = (input) => {
  var doc = new DOMParser().parseFromString(input, "text/html");
  return doc.documentElement.textContent;
};

export const domForHtml = (html) => {
  if (
    typeof DOMParser !== "undefined" &&
    window.DOMParser.prototype.parseFromString
  ) {
    const parser = new window.DOMParser();
    const parsed = parser.parseFromString(html, "text/html");
    if (parsed && parsed.body) {
      return parsed.body;
    }
  }

  // DOMParser support is not present or non-standard
  const newDoc = document.implementation.createHTMLDocument("processing doc");
  const dom = newDoc.createElement("div");
  dom.innerHTML = html;

  return dom;
};

export const copyTextToClipboard = async (text) => {
  if ("clipboard" in navigator) {
    return await navigator.clipboard.writeText(text);
  } else {
    return document.execCommand("copy", true, text);
  }
};

export const getMobileDetect = () => {
  const userAgent =
    typeof navigator === "undefined" ? "SSR" : navigator.userAgent;
  const isAndroid = () => {
    return Boolean(userAgent.match(/Android/i));
  };
  const isIos = () => {
    return Boolean(userAgent.match(/iPhone|iPad|iPod/i));
  };
  const isOpera = () => {
    return Boolean(userAgent.match(/Opera Mini/i));
  };
  const isWindows = () => {
    return Boolean(userAgent.match(/IEMobile/i));
  };
  const isSSR = () => {
    return Boolean(userAgent.match(/SSR/i));
  };

  const isMobile = () => {
    return Boolean(isAndroid() || isIos() || isOpera() || isWindows());
  };
  const isDesktop = () => {
    return Boolean(!isMobile() && !isSSR());
  };
  return {
    isMobile,
    isDesktop,
    isAndroid,
    isIos,
    isSSR,
  };
};
export const goBackHistory = (navigate) => {
  if (window.history.length > 2) {
    // if history is not empty, go back:
    navigate(-1);
  } else {
    // go home:
    navigate("/");
  }
};

export const convertPathRealTimeFirebaseDatabase = (path) => {
  // Paths must be non-empty strings and can't contain ".", "#", "$", "[", or "]"
  if (!path || typeof path !== "string") return "";
  
  // "." -> "dot"
  let newPath = path.replace(/\./g, '_dot_');
  // "#" -> "hash"
  newPath = newPath.replace(/#/g, '_hash_');
  // "$" -> "dollar"
  newPath = newPath.replace(/\$/g, '_dollar_');
  // "[" -> "leftb"
  newPath = newPath.replace(/\[/g, '_leftb_');
  // "]" -> "rightb"
  newPath = newPath.replace(/]/g, '_rightb_');

  // Prefix with NAME_PATH_FIREBASE_REALTIME_DATABASE
  if (NAME_PATH_FIREBASE_REALTIME_DATABASE) {
    newPath = `${NAME_PATH_FIREBASE_REALTIME_DATABASE}/${newPath}`;
  }

  return newPath;
}

/**
 * Generate token by tenant using AES encryption
 * 
 * @param {string} tenant 
 * @returns {string}
 */
export const generateTokenByTenant = (tenant, clientWebsite) => {
  const key = CryptoJS.enc.Utf8.parse(SECRET_KEY_CRYPTO_JS);

  const payload = JSON.stringify({
    tenant: tenant,
    client_website_origin: clientWebsite?.origin || '',
    client_website_href: clientWebsite?.href || '',
    timestamp: Date.now()
  });

  const encrypted = CryptoJS.AES.encrypt(payload, key, {
    mode: CryptoJS.mode.ECB,
    padding: CryptoJS.pad.Pkcs7
  }).toString();
  
  return encrypted;
};

export const getNewIdQuestion = () => {
  // Example: 'q_1633024800_abcd1234'
  const timestamp = Math.floor(Date.now() / 1000); // Current timestamp in seconds
  const randomStr = Math.random().toString(36).substring(2, 10); // Random alphanumeric string of length 8
  return `q_${timestamp}_${randomStr}`;
}

export const randomString = (length = 8) => {
  return Math.random().toString(36).substring(2, 2 + length);
}

export const isTelephoneNumber = (str) => {
  // This regex matches various international and local telephone number formats
  const phoneRegex = /^\+?(\d[\d-. ]+)?(\([\d-. ]+\))?[\d-. ]+\d$/;
  return phoneRegex.test(str);
}

export const removeTrailingSlash = (url) => {
  if (typeof url === 'string') {
    return url.replace(/\/+$/, '');
  }
  return url;
}