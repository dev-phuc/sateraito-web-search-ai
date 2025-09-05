// Framework import
import React from "react";

// Redux components

// Hook components

// Context components

// Library imports
// Library IU imports
import { } from "react-bootstrap";

// Components
import SidebarNavSection from "@/desktop/components/sidebar/SidebarNavSection";

// Define the component
const SidebarNav = ({ items }) => {
  // Use default

  // Use hooks state

  // Use state 

  // Constant value

  // Handler method

  // Component return
  return (
    <ul className="sidebar-nav sidebar-main-left">
      {items &&
        items.map((item, key) => (
          <SidebarNavSection
            key={key}
            pages={item.pages}
            title={item.title}
          />
        ))}
    </ul>
  );
};

export default SidebarNav;
