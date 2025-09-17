/* eslint-disable jsx-a11y/anchor-is-valid */
// Framework import
import React, { forwardRef } from "react";
import { useNavigate } from "react-router-dom";

// Zustand components
import useStoreApp from "@/store/app";

// Hook components

// Context components

// Library imports
// Library IU imports
import { Badge, Collapse } from "react-bootstrap";

// const CustomRouterLink = forwardRef((props, ref) => (
//   <React.Fragment ref={ref}>
//     <NavLink {...props} />
//   </React.Fragment>
// ));

// Define the component
const SidebarNavListItem = (props) => {
  const navigate = useNavigate();

  // Use default
  const { title, href, depth = 0, children, icon, badge, open: openProp = false, } = props;

  // Zustand state
  const { pageActive } = useStoreApp();

  // Use state 
  const [open, setOpen] = React.useState(openProp);

  // Constant value

  // Handler method

  /**
   * handleToggle
   * 
   */
  const handleToggle = () => {
    // setOpen((state) => !state);
    if (href) {
      navigate(href);
    }
  };

  if (children) {
    // Component return
    return (
      <li className={`sidebar-item ${open ? "active" : ""}`}>
        <a
          className={`sidebar-link ${open ? "" : "collapsed"}`}
          data-bs-toggle="collapse"
          aria-expanded={open ? "true" : "false"}
          depth={depth}
          onClick={handleToggle}
        >
          {/* {Icon && <Icon className="feather align-middle" />}{" "} */}
          <span className={icon}></span>{" "}
          <span className="align-middle" depth={depth}>
            {title}
          </span>
          {badge && (
            <Badge className="badge-sidebar-primary" bg="" size={18}>
              {badge}
            </Badge>
          )}
          {open ? <div /> : <div />}
        </a>
        <Collapse in={open}>
          <ul className="sidebar-dropdown list-unstyled">{children}</ul>
        </Collapse>
      </li>
    );
  }

  // Component return
  return (
    <li className="sidebar-item">
      <div
        className={`sidebar-link ${(pageActive && pageActive.href === href) ? "active" : ""}`}
        onClick={handleToggle}
        style={{ cursor: 'pointer' }}
      >
        <span className={icon}></span>{" "}
        <span className="align-middle" depth={depth}>
          {title}
        </span>
        {badge && (
          <Badge className="badge-sidebar-primary" bg="" size={18}>
            {badge}
          </Badge>
        )}
      </div>
    </li>
  );
};

export default SidebarNavListItem;
