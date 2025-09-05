// Framework import
import React from "react";
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from "react-router-dom";

// Redux components

// Hook components
import useAuth from "@/hooks/useAuth";

// Library imports
// Library IU imports
import { Nav, Spinner } from "react-bootstrap";
import { Dropdown } from "react-bootstrap";

// Components


import { getMobileDetect } from "@/utils";

// Define the component
const NavbarUser = () => {
  // Use default
  const { t } = useTranslation();
  const navigate = useNavigate();

  // Use hooks state
  const { user, signOut, isLoading } = useAuth();

  // Constant value


  // Handler method
  if (isLoading) {
    return (
      <Spinner animation="border" variant="primary" />
    )
  }

  if (!user) return <></>;

  const { user_info } = user;

  // Component return
  return (
    <Dropdown className="nav-item" align="end">

      <span className="d-sm-inline-block">
        <Dropdown.Toggle as="a" className="nav-link">
          <img
            src={user_info.photo_url}
            className="avatar img-fluid rounded-circle me-1 object-fit-cover"
            alt={user_info.family_name}
          />
          <span>{user_info.family_name}</span>
        </Dropdown.Toggle>
      </span>

      <Dropdown.Menu drop="end">
        <Dropdown.Item onClick={signOut} role="button">
          <span className="mdi mdi mdi-logout align-middle me-2"></span>
          {t("TXT_LOGOUT")}
        </Dropdown.Item>

      </Dropdown.Menu>
    </Dropdown>
  );
};

export default NavbarUser;
