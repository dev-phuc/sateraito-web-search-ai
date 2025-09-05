import React, { useContext } from "react";

import Swal from 'sweetalert2'

import { THEME, NOTIFY_CONFIG } from "@/constants";
import useSettingsState from "@/hooks/useSettingsState";

import ThemeContext from "@/contexts/ThemeContext";
import NotyfContext from "@/contexts/NotyfContext";

function ThemeProvider({ children }) {
  const [theme, setTheme] = useSettingsState("theme", THEME.DEFAULT);
  const [skinColor, setSkinColor] = useSettingsState(
    "themeSkinColor",
    THEME.SKIN_COLOR_DEFAULT
  );
  const notyf = useContext(NotyfContext);

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

  const confirmRejoin = (callback) => {
    Swal.fire({
      title: 'Are you sure?',
      text: "Would you like to rejoin this book?",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes, I would!'
    }).then((result) => {
      if (result.isConfirmed) {
        callback(true);
        return;
      }

      callback(false);
    })
  }

  const confirmEditBook = (callback) => {
    Swal.fire({
      title: 'Are you sure?',
      text: "Would you like to edit this book?",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes, I would!'
    }).then((result) => {
      if (result.isConfirmed) {
        callback(true);
        return;
      }

      callback(false);
    })
  }

  const confirmDeleteBook = (callback) => {
    Swal.fire({
      title: 'Are you sure?',
      text: "Would you like to move this book to the trash?",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes, I would!'
    }).then((result) => {
      if (result.isConfirmed) {
        callback(true);
        return;
      }

      callback(false);
    })
  }

  const confirmRemoveStoryShared = (callback) => {
    Swal.fire({
      title: 'Are you sure?',
      text: "Do you want to delete this shared information?",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes, I would!'
    }).then((result) => {
      if (result.isConfirmed) {
        callback(true);
        return;
      }

      callback(false);
    })
  }

  const confirmDisableAccount = (isSetDisable, callback) => {
    Swal.fire({
      title: 'Are you sure?',
      text: isSetDisable ? "Do you want to disable Account selected?" : "Do you want to enable Account selected?",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes, I would!'
    }).then((result) => {
      if (result.isConfirmed) {
        callback(true);
        return;
      }

      callback(false);
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
        confirmRejoin,
        confirmEditBook,
        confirmDeleteBook,
        confirmRemoveStoryShared,
        confirmDisableAccount,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

export default ThemeProvider;
