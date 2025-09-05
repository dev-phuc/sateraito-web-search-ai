// Framework import
import React from "react";
import { useLocation } from "react-router-dom";

// Redux components

// Hook components

// Context components

// Library imports
// Library IU imports
import { } from "react-bootstrap";

// Components
import reduceChildRoutes from "@/desktop/components/sidebar/reduceChildRoutes";

// Define the component
const SidebarNavList = (props) => {
  // Use default
  const { pages, depth } = props;

  // Use hooks state

  // Use state 

  // Constant value
  const router = useLocation();
  const currentRoute = router.pathname;
  const childRoutes = pages.reduce(
    (items, page) => reduceChildRoutes({ items, page, currentRoute, depth }),
    []
  );

  // Component return
  return <React.Fragment>{childRoutes}</React.Fragment>;
};

export default SidebarNavList;
