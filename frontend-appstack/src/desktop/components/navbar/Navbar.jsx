// Framework import
import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";

// Zustand
import useAppStore from "@/store/app";

// Hook components
import useAuth from "@/hooks/useAuth";
import useSidebar from "@/hooks/useSidebar";

// Context components

// Library imports
// Library IU imports
import { Button, Navbar, Nav, Form, InputGroup } from "react-bootstrap";
import { OverlayTrigger, Tooltip } from "react-bootstrap";
import {
  AlertCircle,
  Bell,
  BellOff,
  Home,
  MessageCircle,
  UserPlus,
  Search,
} from "react-feather";

// Components
import NavbarDropdown from "@/desktop/components/navbar/NavbarDropdown";
import NavbarDropdownItem from "@/desktop/components/navbar/NavbarDropdownItem";
import NavbarLanguages from "@/desktop/components/navbar/NavbarLanguages";
import NavbarUser from "./NavbarUser";
import NavbarSearch from "./NavbarSearch";
import SidebarOffCanvas from "../sidebar/SidebarOffCanvas";

const notifications = [
  {
    type: "important",
    title: "Update completed",
    description: "Restart server 12 to complete the update.",
    time: "2h ago",
  },
  {
    type: "default",
    title: "Lorem ipsum",
    description: "Aliquam ex eros, imperdiet vulputate hendrerit et.",
    time: "6h ago",
  },
  {
    type: "login",
    title: "Login from 192.186.1.1",
    description: "",
    time: "6h ago",
  },
  {
    type: "request",
    title: "New connection",
    description: "Anna accepted your request.",
    time: "12h ago",
  },
];

import avatar1 from "@/assets/img/avatars/avatar.jpg";
import avatar3 from "@/assets/img/avatars/avatar-3.jpg";
import avatar4 from "@/assets/img/avatars/avatar-4.jpg";
import avatar5 from "@/assets/img/avatars/avatar-5.jpg";

const messages = [
  {
    name: "Ashley Briggs",
    avatar: avatar5,
    description: "Nam pretium turpis et arcu. Duis arcu tortor.",
    time: "15m ago",
  },
  {
    name: "Chris Wood",
    avatar: avatar1,
    description: "Curabitur ligula sapien euismod vitae.",
    time: "2h ago",
  },
  {
    name: "Stacie Hall",
    avatar: avatar4,
    description: "Pellentesque auctor neque nec urna.",
    time: "4h ago",
  },
  {
    name: "Bertha Martin",
    avatar: avatar3,
    description: "Aenean tellus metus, bibendum sed, posuere ac, mattis non.",
    time: "5h ago",
  },
];

// Define the component
const NavbarComponent = () => {
  // Use default
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();

  // Zustand state
  const { pageActive } = useAppStore();

  // Use hooks state
  const { isOpen, setIsOpen } = useSidebar();
  const { isInitialized, user, isLoading } = useAuth();

  // Use state 
  const [keyword, setKeyword] = useState('');

  // Constant value

  // Handler method

  /**
   * Handler submit search
   * 
   * @param {Event} event 
   */
  const handlerSubmitSearch = (event) => {
    event.preventDefault();
    if (location.pathname != 'search') {
      navigate({
        pathname: '/search',
        search: '?keyword=' + keyword.trim()
      });
    } else {
      navigate({
        search: '?keyword=' + keyword.trim()
      });
    }
  }

  // Component return
  return (
    <Navbar variant="light" expand className="navbar-bg">
      <span className="sidebar-toggle me-0 d-flex" onClick={() => { setIsOpen(!isOpen); }}>
        <i className="mdi mdi-menu align-self-center" />
      </span>

      <div className="page-header">
        <h1 className="text h3 d-inline align-middle">
          {t(pageActive.title)}
        </h1>
      </div>

      <Navbar.Collapse>
        <Nav className="navbar-align">
          {/* <NavbarLanguages /> */}
          <NavbarUser />
        </Nav>
      </Navbar.Collapse>
    </Navbar>
  );
};

export default NavbarComponent;
