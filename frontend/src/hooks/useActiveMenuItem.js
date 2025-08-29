import { useState, useEffect } from 'react';
import { useLocation, useParams } from 'react-router';

/**
 * Custom hook to manage active menu item based on current route
 * @returns {string} activeKey - The key of the currently active menu item
 */
const useActiveMenuItem = (menuItems) => {
  const location = useLocation();
  const { storeCode } = useParams();
  const [activeKey, setActiveKey] = useState('');

  useEffect(() => {
    if (!menuItems || menuItems.length === 0) {
      return;
    }

    const path = location.pathname;
    let foundItem = null;

    // Function to find menu item by path
    const findMenuItemByPath = (items, targetPath) => {
      for (const item of items) {
        // Check exact match
        if (item.pathname === targetPath) {
          return item;
        }
        
        // Check children if exists
        if (item.children) {
          const childMatch = findMenuItemByPath(item.children, targetPath);
          if (childMatch) {
            return childMatch;
          }
        }
      }
      return null;
    };

    // Try to find exact match first
    foundItem = findMenuItemByPath(menuItems, path);

    // If no exact match found, try to find closest parent route
    if (!foundItem && path.includes('/store/')) {
      const pathSegments = path.split('/');
      
      // Try removing segments from the end until we find a match
      for (let i = pathSegments.length; i >= 3; i--) {
        const parentPath = pathSegments.slice(0, i).join('/');
        foundItem = findMenuItemByPath(menuItems, parentPath);
        if (foundItem) {
          break;
        }
      }
    }

    // Set active key
    if (foundItem) {
      setActiveKey(foundItem.key);
    } else if (menuItems.length > 0) {
      // Default to dashboard if available
      const dashboardItem = menuItems.find(item => 
        item.key === 'admin_dashboard' || 
        item.pathname === `/store/${storeCode}/admin`
      );
      setActiveKey(dashboardItem ? dashboardItem.key : menuItems[0].key);
    }
  }, [location.pathname, menuItems, storeCode]);

  return activeKey;
};

export default useActiveMenuItem;
