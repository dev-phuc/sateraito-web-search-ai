import { useEffect } from "react";
import useLocalStorage from "./useLocalStorage";
import { getMobileDetect } from "@/utils";

function useSettingsState(key, initialValue) {
  const [value, setValue] = useLocalStorage(key, initialValue);
  const device = getMobileDetect();

  useEffect(() => {
    // Set data attribute on body element
    document.body.dataset[key] = value;

    // console.log("useSettingsState", key, initialValue);

    // Replace them skin color
    if (key === "themeSkinColor") {
      document.documentElement.style.setProperty("--base-color", value);
    }

    // Replace stylesheet if dark theme gets toggled
    if (key === "theme") {
      console.log(key);
      const theme = value === "dark" ? "dark" : "light";

      let stylesheet = document.querySelector(".js-stylesheet");
      if (!stylesheet) {
        stylesheet = document.createElement("link");
        stylesheet.setAttribute("class", "js-stylesheet");
      }
      if (!device.isMobile()) {
      if (import.meta.env.PROD) {
        // Use precompiled css files while in production mode
        stylesheet.setAttribute(
          "href",
          `${import.meta.env.VITE_BASE}/assets/${theme}.${
            import.meta.env.VITE_VERSION_JS
          }.css`
        );
      } else {
        // Use sass files while in development mode, so we can watch changes while developing
        stylesheet.setAttribute("href", `/src/assets/scss/${theme}.scss`);
      }
      } else {
        if (import.meta.env.PROD) {
          // Use precompiled css files while in production mode
          stylesheet.setAttribute(
            "href",
            `${import.meta.env.VITE_BASE}/assets/mobile_${theme}.${
              import.meta.env.VITE_VERSION_JS
            }.css`
          );
        } else {
          // Use sass files while in development mode, so we can watch changes while developing
          stylesheet.setAttribute(
            "href",
            `/src/assets/scss/mobile_${theme}.scss`
          );
        }
      }

      // if (!device.isMobile()) {
      //   if (import.meta.env.PROD) {
      //     // Use precompiled css files while in production mode
      //     stylesheet.setAttribute(
      //       "href",
      //       `${import.meta.env.VITE_BASE}/assets/${theme}.${
      //         import.meta.env.VITE_VERSION_JS
      //       }.css`
      //     );
      //   } else {
      //     // Use sass files while in development mode, so we can watch changes while developing
      //     stylesheet.setAttribute("href", `/src/assets/scss/${theme}.scss`);
      //   }
      // } else {
      //   if (import.meta.env.PROD) {
      //     // Use precompiled css files while in production mode
      //     stylesheet.setAttribute(
      //       "href",
      //       `${import.meta.env.VITE_BASE}/assets/mobile_${theme}.${
      //         import.meta.env.VITE_VERSION_JS
      //       }.css`
      //     );
      //   } else {
      //     // Use sass files while in development mode, so we can watch changes while developing
      //     stylesheet.setAttribute(
      //       "href",
      //       `/src/assets/scss/mobile_${theme}.scss`
      //     );
      //   }
      // }
      document.head.appendChild(stylesheet);
    }
  }, [value, key]);

  return [value, setValue];
}

export default useSettingsState;
