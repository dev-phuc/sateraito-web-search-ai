// Framework import
import React from "react";
import classNames from "classnames";

// Define the component
const Main = ({ className, children }) => (
  <div className={classNames("main", className)}>{children}</div>
);

export default Main;
