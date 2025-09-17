import React, { useContext } from "react";

import Swal from 'sweetalert2'

import { THEME, NOTIFY_CONFIG } from "@/constants";
import useSettingsState from "@/hooks/useSettingsState";

import ThemeContext from "@/contexts/ThemeContext";
import NotyfContext from "@/contexts/NotyfContext";

function ThemeProvider({ children }) {
  const notyf = useContext(NotyfContext);

  const [theme, setTheme] = useSettingsState("theme", THEME.DEFAULT);
  const [skinColor, setSkinColor] = useSettingsState("themeSkinColor", THEME.SKIN_COLOR_DEFAULT);

  /**
 * Show notice
 * @param {String} message 
 */
  const showNotice = (type, message, duration, ripple, dismissible, px, py) => {
    notyf.open({
      type: type,
      message: message,
      duration: duration || NOTIFY_CONFIG.DURATION,
      ripple: ripple || NOTIFY_CONFIG.RIPPLE,
      dismissible: dismissible || NOTIFY_CONFIG.DISMISSIBLE,
      position: {
        x: px || NOTIFY_CONFIG.POSITION.LEFT,
        y: py || NOTIFY_CONFIG.POSITION.BOTTOM,
      },
    })
  }

  return (
    <ThemeContext.Provider
      value={{
        theme,
        setTheme,
        skinColor,
        setSkinColor,
        showNotice,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

export default ThemeProvider;
