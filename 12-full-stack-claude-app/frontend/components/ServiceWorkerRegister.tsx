"use client";

import { useEffect } from "react";

/**
 * Registers public/sw.js on mount. A separate client component (rather
 * than putting this logic in layout.tsx directly) because layout.tsx is
 * a server component -- browser-only APIs like navigator.serviceWorker
 * can only run in a client component.
 */
export default function ServiceWorkerRegister() {
  useEffect(() => {
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("/sw.js").catch(() => {
        // Registration failing (e.g. unsupported browser) isn't fatal --
        // the app still works as a normal website, just not installable.
      });
    }
  }, []);

  return null;
}
