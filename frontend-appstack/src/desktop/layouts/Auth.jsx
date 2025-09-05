// Framework import
import React, { Suspense, useState, useEffect } from "react";
import { Outlet, useNavigate, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

// Redux components

// Hook components
import useAuth from "@/hooks/useAuth";

// Context components

// Library imports
// Library IU imports

// Components

// Define the component
const AuthLayout = ({ children }) => {
  // Use default
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { tenant, app_id } = useParams();

  // Use hooks state
  const { setTenantAppId, isInitialized } = useAuth();

  // Use state 
  const processOnChangeTenantAppId = async (tenant, app_id) => {
    setTenantAppId(tenant, app_id);
  }

  useEffect(() => {
    processOnChangeTenantAppId(tenant, app_id);
  }, [tenant, app_id]);

  // Component return
  return (
    <>
      {children}
      <Outlet />
    </>
  )
};

export default AuthLayout;
