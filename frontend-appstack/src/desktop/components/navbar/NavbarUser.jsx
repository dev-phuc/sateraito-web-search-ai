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
  const { user, signOut, isCreator, isAdmin, isLoading } = useAuth();

  // Constant value


  // Handler method
  if (isLoading) {
    return (
      <Spinner animation="border" variant="primary" />
    )
  }

  console.log(user);
  
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

        <Link data-rr-ui-dropdown-item to="/setting" tole="button" className="dropdown-item">
          <span className="mdi mdi-cog-outline align-middle me-2"></span>
          {t("TXT_SETTING")}
        </Link>

        <Dropdown.Divider />
        <Dropdown.Item href="/auth/logout">
          <span className="mdi mdi mdi-logout align-middle me-2"></span>
          {t("BTN_SIGN_OUT")}
        </Dropdown.Item>

      </Dropdown.Menu>
    </Dropdown>
  );
};

export default NavbarUser;
