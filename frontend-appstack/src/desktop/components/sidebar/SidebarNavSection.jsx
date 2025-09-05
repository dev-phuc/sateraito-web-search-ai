// Framework import
import React from "react";

// Redux components

// Hook components

// Context components

// Library imports
// Library IU imports

// Components
import SidebarNavList from "@/desktop/components/sidebar/SidebarNavList";

const SidebarNavSection = (props) => {
  // Use default
  const { title, pages, className, ...rest } = props;
  
  // Component return
  return (
    <React.Fragment {...rest}>
      {title && <li className="sidebar-header">{title}</li>}
      <SidebarNavList pages={pages} depth={0} />
    </React.Fragment>
  );
};

export default SidebarNavSection;
