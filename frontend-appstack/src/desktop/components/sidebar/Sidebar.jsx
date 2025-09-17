// // Framework import
// import React from "react";
// import { Link, useNavigate } from "react-router-dom";

// // Redux components

// // Hook components
// import useSidebar from "@/hooks/useSidebar";

// // Context components

// // Library imports
// import PerfectScrollbar from "react-perfect-scrollbar";
// // Library IU imports
// import { Spinner } from "react-bootstrap";

// // Components
// import SidebarFooter from "@/mobile/components/sidebar/SidebarFooter";
// import SidebarNav from "@/mobile/components/sidebar/SidebarNav";
// import { ReactComponent as Logo } from "@/assets/img/logo.svg";

// // Define the component
// const Sidebar = ({ items, isLoading, showFooter = true }) => {
//   // Use default
//   const navigate = useNavigate();

//   // Use hooks state
//   const { isOpen } = useSidebar();

//   // Use state

//   // Constant value

//   // Handler method

//   // Component return
//   return (
//     <nav className={`sidebar ${!isOpen ? "collapsed" : ""}`}>
//       <div className="sidebar-content sidebar-custom">
//         {/* <PerfectScrollbar> */}
//         <div className="wrap-header-static">
//           <Link className="sidebar-brand text-start mb-2" to={'/'}>
//             <Logo />
//           </Link>
//         </div>
//         <SidebarNav items={items} />

//         {isLoading && <>
//           <div className="text-center">
//             <Spinner />
//           </div>
//         </>}

//         {!!showFooter && <SidebarFooter />}
//         {/* </PerfectScrollbar> */}
//       </div>
//     </nav>
//   );
// };

// export default Sidebar;


// Framework import
import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

// Redux components

// Hook components
import useSidebar from "@/hooks/useSidebar";

// Context components

// Library imports
import PerfectScrollbar from "react-perfect-scrollbar";
// Library IU imports
import { Spinner } from "react-bootstrap";

import { ReactComponent as Logo } from "@/assets/img/logo.svg";
import { ReactComponent as LogoC } from "@/assets/img/logo_circle.svg";

// Components
import SidebarHeader from "./SidebarHeader";
import SidebarFooter from "@/desktop/components/sidebar/SidebarFooter";
import SidebarNav from "@/desktop/components/sidebar/SidebarNav";

// Define the component
const Sidebar = ({ items, isLoading, showFooter = true }) => {
  // Use default
  const { t } = useTranslation();
  const navigate = useNavigate();

  // Use hooks state
  const { isOpen } = useSidebar();

  // Use state

  // Constant value

  // Handler method

  // Component return
  return (
    <nav className={`sidebar ${!isOpen ? "collapsed" : ""}`}>
      <div className="sidebar-content sidebar-custom">

        <PerfectScrollbar>

          <div className="wrap-header-static mb-3">
            <div className="sidebar-brand" to="/" tabIndex={-1}>
              <Logo className="normal-logo" style={{ width: '100%' }} />
              {/* <span className="align-middle me-3">{ t("AI_BOARD_TITLE") }</span> */}
              <LogoC className="compact-logo" style={{ width: '100%' }} />
            </div>
          </div>

          <SidebarNav items={items} />

          {isLoading && <>
            <div className="text-center">
              <Spinner />
            </div>
          </>}

          {!!showFooter && <SidebarFooter />}
        </PerfectScrollbar>
      </div>
    </nav>
  );
};

export default Sidebar;
