/**
 * Human-friendly labels for the backend's topic slugs. Shared between the
 * main page's dropdown and the upload modal so both stay in sync -- if the
 * backend's /topics list ever grows, an unmapped slug just falls back to
 * showing its raw value instead of breaking.
 */
export const TOPIC_LABELS: Record<string, string> = {
  dwdm_osnr: "DWDM / OSNR",
  ethernet: "Ethernet",
  ip: "IP",
  others: "Others",
};
