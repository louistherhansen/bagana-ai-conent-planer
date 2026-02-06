/**
 * React Hook for Dynamic Logo Configuration
 * 
 * This hook can be extended to fetch logo config from an API
 * or database in the future.
 */

import { useState, useEffect } from "react";
import { getLogoConfig, type LogoConfig, LOGO_CONFIG } from "@/lib/logo-config";

export function useLogo(autoRefresh = false) {
  const [config, setConfig] = useState<LogoConfig>(getLogoConfig());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const refresh = async () => {
    setLoading(true);
    setError(null);
    try {
      // In the future, this can fetch from an API
      // const response = await fetch('/api/logo-config');
      // const data = await response.json();
      // setConfig(data);
      
      // For now, use the config
      setConfig(getLogoConfig());
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Failed to load logo configuration"));
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
    config,
    loading,
    error,
    refresh,
    // Direct access to config for mutations
    configSource: LOGO_CONFIG,
  };
}
