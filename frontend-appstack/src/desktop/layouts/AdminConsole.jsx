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
import Wrapper from "@/desktop/components/Wrapper";
import Sidebar from "@/desktop/components/sidebar/Sidebar";
import Main from "@/desktop/components/Main";
import Navbar from "@/desktop/components/navbar/Navbar";
import Content from "@/desktop/components/Content";
// import Footer from "@/desktop/components/Footer";
// import Settings from "@/desktop/components/Settings";
import OffCanvasSettingTheme from "@/desktop/components/OffCanvasSettingTheme";
import Loader from "@/desktop/components/Loader";
// import navAdminItems from "@/desktop/components/sidebar/dashboardAdminItems";


// Define the component
const AdminConsoleLayout = ({ children }) => {
  // Use default
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { tenant, app_id } = useParams();

  // Use hooks state
  const { isInitialized, initializeAuth, isCreator, isAdmin } = useAuth();

  // Use state 
  const [dashboardItems, setDashboardItems] = useState([
    {
      pages: [
        {
          href: `/${tenant}/${app_id}/admin_console/dashboard`,
          title: t('TXT_DASHBOARD'),
          icon: 'mdi mdi-view-dashboard-outline me-2',
        },
        {
          href: `/${tenant}/${app_id}/admin_console/domains`,
          title: t('TXT_DOMAINS_MANAGEMENT'),
          icon: 'mdi mdi-earth me-2',
        },
        {
          href: `/${tenant}/${app_id}/admin_console/design-search-box`,
          title: t('TXT_DESIGN_SEARCH_BOX'),
          icon: 'mdi mdi-magnify me-2',
        },
        {
          href: `/${tenant}/${app_id}/admin_console/box-search-encoder`,
          title: t('TXT_ENCODER_HTML_JS'),
          icon: 'mdi mdi-code-tags me-2',
        },
        {
          href: `/${tenant}/${app_id}/admin_console/design-banner`,
          title: t('TXT_DESIGN_BANNER_KEYWORDS'),
          icon: 'mdi mdi-image-area me-2',
        },
        {
          href: `/${tenant}/${app_id}/admin_console/ai-configuration`,
          title: t('TXT_AI_CONFIGURATION'),
          icon: 'mdi mdi-robot-outline me-2',
        },
        {
          href: `/${tenant}/${app_id}/admin_console/logs`,
          title: t('TXT_OPERATIONS_LOGS'),
          icon: 'mdi mdi-file-document-outline me-2',
        },
        {
          href: `/${tenant}/${app_id}/admin_console/usage`,
          title: t('TXT_USAGE_STATISTICS'),
          icon: 'mdi mdi-chart-bar me-2',
        },
      ],
    },
  ]);

  useEffect(() => {
    initializeAuth(tenant, app_id);
  }, [tenant, app_id]);

  if (!isInitialized) {
    return <></>
  }

  // Component return
  return (
    <React.Fragment>

      <Wrapper>
        <Sidebar items={dashboardItems} showFooter={false} />

        <Main>
          <Navbar />

          <Content>
            <Suspense fallback={<Loader />}>

              {children}
              <Outlet />

            </Suspense>
          </Content>

          {/*<Footer />*/}
        </Main>

      </Wrapper>

      <OffCanvasSettingTheme></OffCanvasSettingTheme>

    </React.Fragment>
  )
};

export default AdminConsoleLayout;
