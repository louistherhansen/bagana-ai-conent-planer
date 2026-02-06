/**
 * React Hook for Dynamic Navigation Items
 * 
 * This hook can be extended to fetch menu items from an API
 * or database in the future.
 */

import { useState, useEffect } from "react";
import { getNavItems, type NavItem, NAV_CONFIG } from "@/lib/nav-config";

export function useNavItems(autoRefresh = false) {
  const [items, setItems] = useState<NavItem[]>(getNavItems());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const refresh = async () => {
    setLoading(true);
    setError(null);
    try {
      // In the future, this can fetch from an API
      // const response = await fetch('/api/nav-items');
      // const data = await response.json();
      // setItems(data);
      
      // For now, use the config
      setItems(getNavItems());
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Failed to load navigation items"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (autoRefresh) {
      refresh();
    }
  }, [autoRefresh]);

  return {
    items,
    loading,
    error,
    refresh,
    // Direct access to config for mutations
    config: NAV_CONFIG,
  };
}
