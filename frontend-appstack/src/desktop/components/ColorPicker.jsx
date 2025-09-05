import React, { useState, useEffect, useContext } from "react";
import { useTranslation } from "react-i18next";
import { CirclePicker } from "react-color";
import useTheme from "@/hooks/useTheme";

const ColorSetting = (props) => {
  const { onChange } = props;
  const { t } = useTranslation();
  const { skinColor, setSkinColor } = useTheme();
  const handleChangeComplete = (color) => {
    setSkinColor(color.hex);
    document.documentElement.style.setProperty("--base-color", color.hex);
    onChange();
  };
  return (
    <React.Fragment>
      <CirclePicker color={skinColor} onChangeComplete={handleChangeComplete} />
    </React.Fragment>
  );
};
ColorSetting.defaultProps = {
  onChange: () => {},
};

export default ColorSetting;
