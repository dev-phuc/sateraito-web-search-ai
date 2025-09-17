// Framework import
import React, { Suspense, useState, useEffect } from "react";
import { Outlet, useNavigate, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

// Zustand
import useAppStore from "@/store/app";

// Hook components
import useConfig from "@/hooks/useUserConfig";
import useAuth from "@/hooks/useAuth";
import useTheme from "@/hooks/useTheme";
import useSidebar from "@/hooks/useSidebar";
import useLayout from "@/hooks/useLayout";

// Library imports
// Library IU imports

// Components
import Wrapper from "@/desktop/components/Wrapper";
import Sidebar from "@/desktop/components/sidebar/Sidebar";
import Main from "@/desktop/components/Main";
import Navbar from "@/desktop/components/navbar/Navbar";
import Content from "@/desktop/components/Content";
import OffCanvasSettingTheme from "@/desktop/components/OffCanvasSettingTheme";
import Loader from "@/desktop/components/Loader";

// Define the component
const AdminConsoleLayout = ({ children }) => {
  // Use default
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { tenant, app_id } = useParams();

  // Zustand state
  const { pageActive, setPageActive } = useAppStore();

  // Use hooks state
  const { getUserConfig } = useConfig();
  const { setTheme } = useTheme();
  const { setPosition, setBehavior } = useSidebar();
  const { setLayout } = useLayout();
  const { setTenantAppId, isInitialized, initializeAuth } = useAuth();

  // Use state 
  const [dashboardItems, setDashboardItems] = useState([
    {
      pages: [
        {
          href: `/${tenant}/${app_id}/admin_console`,
          title: 'TXT_DASHBOARD',
          icon: 'mdi mdi-view-dashboard-outline me-2',
        },
        {
          href: `/${tenant}/${app_id}/admin_console/domains`,
          title: 'TXT_DOMAINS_MANAGEMENT',
          icon: 'mdi mdi-earth me-2',
        },
        {
          href: `/${tenant}/${app_id}/admin_console/box-search-config`,
          title: 'TXT_DESIGN_SEARCH_BOX',
          icon: 'mdi mdi-lead-pencil me-2',
        },
        {
          href: `/${tenant}/${app_id}/admin_console/design-banner`,
          title: 'TXT_DESIGN_BANNER_KEYWORDS',
          icon: 'mdi mdi-image-area me-2',
        },
        {
          href: `/${tenant}/${app_id}/admin_console/ai-configuration`,
          title: 'TXT_AI_CONFIGURATION',
          icon: 'mdi mdi-robot-outline me-2',
        },
        {
          href: `/${tenant}/${app_id}/admin_console/logs`,
          title: 'TXT_OPERATIONS_LOGS',
          icon: 'mdi mdi-file-document-outline me-2',
        },
        {
          href: `/${tenant}/${app_id}/admin_console/usage`,
          title: 'TXT_USAGE_STATISTICS',
          icon: 'mdi mdi-chart-bar me-2',
        },
        {
          href: `/${tenant}/${app_id}/admin_console/setting`,
          title: 'TXT_SETTINGS',
          icon: 'mdi mdi-cog-outline me-2',
        },
      ],
    },
  ]);

  // Handlers
  const processLoadUserConfig = async () => {
    try {
      const data = await getUserConfig(tenant, app_id);
      if (data) {
        const { config } = data;
        if (config) {
          const { theme, sidebar_position, sidebar_behavior, layout } = config;
          if (theme) {
            setTheme(theme);
          }
          if (sidebar_position) {
            setPosition(sidebar_position);
          }
          if (sidebar_behavior) {
            setBehavior(sidebar_behavior);
          }
          if (layout) {
            setLayout(layout);
          }
        }
      }
    } catch (error) {
      console.error("Failed to load user config:", error);
    }
  };

  useEffect(() => {
    setTenantAppId(tenant, app_id);
  }, [tenant, app_id]);

  useEffect(() => {
    if (isInitialized) {
      processLoadUserConfig();
    }
  }, [isInitialized]);

  useEffect(() => {
    // Update page active
    let pages = dashboardItems[0].pages;

    let foundPage = pages.find((page) => window.location.pathname === page.href);
    if (foundPage) {
      setPageActive(foundPage);
    } else {
      setPageActive(null);
    }

  }, [navigate]);

  if (!isInitialized) {
    return <>Loading...</>
  }

  // Component return
  return (
    <>

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
    </>
  )
};

export default AdminConsoleLayout;
