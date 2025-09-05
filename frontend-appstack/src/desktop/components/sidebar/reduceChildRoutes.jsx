// Framework import
import React from "react";
import { matchPath } from "react-router-dom";

// Redux components

// Hook components

// Context components

// Library imports
// Library IU imports

// Components
import SidebarNavListItem from "@/desktop/components/sidebar/SidebarNavListItem";
import SidebarNavList from "@/desktop/components/sidebar/SidebarNavList";

// Define the component
const reduceChildRoutes = (props) => {
  // Use default
  const { items, page, depth, currentRoute } = props;

  if (page.children) {
    const open = page.href
      ? !!matchPath(
          {
            path: page.href,
            end: false,
          },
          currentRoute
        )
      : false;

    items.push(
      <SidebarNavListItem
        depth={depth}
        icon={page.icon}
        iconcls={page.iconcls}
        key={page.title}
        badge={page.badge}
        open={!!open}
        title={page.title}
        href={page.href}
        customCls={page.customCls ? page.customCls : ""}
        groupColor={page.groupColor ? page.groupColor : ""}
        cls={page.cls}
      >
        <SidebarNavList depth={depth + 1} pages={page.children} />
      </SidebarNavListItem>
    );
  } else {
    items.push(
      <SidebarNavListItem
        depth={depth}
        href={page.href}
        icon={page.icon}
        iconcls={page.iconcls}
        key={page.title}
        badge={page.badge}
        title={page.title}
        customCls={page.customCls ? page.customCls : ""}
        groupColor={page.groupColor ? page.groupColor : ""}
        cls={page.cls}
      />
    );
  }

  // Component return
  return items;
};

export default reduceChildRoutes;
