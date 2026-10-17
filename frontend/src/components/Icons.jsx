/**
 * Lightweight inline SVG icon set — no icon library required.
 * All icons are currentColor-based so they inherit text color.
 */
import React from 'react';

const base = { fill: 'none', stroke: 'currentColor', strokeWidth: 1.8, strokeLinecap: 'round', strokeLinejoin: 'round' };

export const IconDashboard = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <rect x="3" y="3" width="7.5" height="7.5" rx="1.6" />
    <rect x="13.5" y="3" width="7.5" height="7.5" rx="1.6" />
    <rect x="3" y="13.5" width="7.5" height="7.5" rx="1.6" />
    <rect x="13.5" y="13.5" width="7.5" height="7.5" rx="1.6" />
  </svg>
);

export const IconUsers = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <circle cx="9" cy="8" r="3.4" />
    <path d="M2.8 19.6c.7-3.1 3.2-5 6.2-5s5.5 1.9 6.2 5" />
    <circle cx="17.4" cy="9" r="2.5" />
    <path d="M16.2 14.9c2.6.2 4.4 1.7 5 4.7" />
  </svg>
);

export const IconMic = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <rect x="9" y="2.8" width="6" height="11" rx="3" />
    <path d="M5.5 11a6.5 6.5 0 0 0 13 0" />
    <path d="M12 17.5v3.7M8.7 21.2h6.6" />
  </svg>
);

export const IconPhone = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <path d="M6.6 3.5H9l1.4 4.2-2.1 1.6a12 12 0 0 0 4.9 4.9l1.6-2.1 4.2 1.4v2.4a2 2 0 0 1-2.2 2A15.4 15.4 0 0 1 4.6 5.7a2 2 0 0 1 2-2.2Z" />
  </svg>
);

export const IconCalendar = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <rect x="3.5" y="5" width="17" height="16" rx="2" />
    <path d="M3.5 10h17M8 2.8V6.4M16 2.8V6.4" />
  </svg>
);

export const IconMail = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <rect x="3" y="5" width="18" height="14" rx="2" />
    <path d="m3.8 6.6 8.2 6.2 8.2-6.2" />
  </svg>
);

export const IconGlobe = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <circle cx="12" cy="12" r="9" />
    <path d="M3 12h18M12 3c2.6 2.6 2.6 15.4 0 18M12 3c-2.6 2.6-2.6 15.4 0 18" />
  </svg>
);

export const IconUser = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <circle cx="12" cy="8" r="3.8" />
    <path d="M4.5 20.4c.9-3.9 3.9-6.2 7.5-6.2s6.6 2.3 7.5 6.2" />
  </svg>
);

export const IconBuilding = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <rect x="5" y="3.5" width="14" height="17" rx="1.8" />
    <path d="M9 7.2h2M13 7.2h2M9 11h2M13 11h2M10 20.5v-3.4h4v3.4" />
  </svg>
);

export const IconShield = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <path d="M12 2.8 19.5 6v5.4c0 4.6-3.1 8-7.5 9.8-4.4-1.8-7.5-5.2-7.5-9.8V6L12 2.8Z" />
    <path d="M9.2 11.6 11.2 13.6 15 9.8" />
  </svg>
);

export const IconHeartAlert = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <path d="M12 20.6C7.2 17.4 3.6 14.4 3.6 10.2A4.6 4.6 0 0 1 12 7.4a4.6 4.6 0 0 1 8.4 2.8c0 4.2-3.6 7.2-8.4 10.4Z" />
    <path d="M12 8.6v4M12 15.4v.2" />
  </svg>
);

export const IconSearch = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <circle cx="11" cy="11" r="6.4" />
    <path d="m16 16 4.4 4.4" />
  </svg>
);

export const IconPlus = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <path d="M12 4.5v15M4.5 12h15" />
  </svg>
);

export const IconEdit = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <path d="M4 20h4.2L20 8.2a2.3 2.3 0 0 0-3.2-3.2L5 16.8 4 20Z" />
  </svg>
);

export const IconTrash = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <path d="M4 6.8h16M9.5 6.8V4.6a1 1 0 0 1 1-1h3a1 1 0 0 1 1 1v2.2M6.2 6.8l.8 12.2a2 2 0 0 0 2 1.8h6a2 2 0 0 0 2-1.8l.8-12.2" />
  </svg>
);

export const IconArrow = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <path d="M4.5 12h14M13 6.5l5.5 5.5L13 17.5" />
  </svg>
);

export const IconEye = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <path d="M2.5 12S6 5.8 12 5.8 21.5 12 21.5 12 18 18.2 12 18.2 2.5 12 2.5 12Z" />
    <circle cx="12" cy="12" r="2.8" />
  </svg>
);

export const IconChat = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <path d="M4 4.5h16a1.5 1.5 0 0 1 1.5 1.5v9a1.5 1.5 0 0 1-1.5 1.5H9l-4.5 3.6V16.5H4A1.5 1.5 0 0 1 2.5 15V6A1.5 1.5 0 0 1 4 4.5Z" />
    <path d="M8 9h8M8 12.4h5" />
  </svg>
);

export const IconChip = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <rect x="6" y="6" width="12" height="12" rx="2" />
    <rect x="9.5" y="9.5" width="5" height="5" rx="1" />
    <path d="M9 2.8V6M15 2.8V6M9 18v3.2M15 18v3.2M2.8 9H6M2.8 15H6M18 9h3.2M18 15h3.2" />
  </svg>
);

export const IconPlug = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <path d="M9 2.8v5M15 2.8v5M6.5 7.8h11v2.8a5.5 5.5 0 0 1-11 0V7.8ZM12 16.1v5.1" />
  </svg>
);

export const IconHook = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <path d="M12 2.8v8.4M8 15.4a4 4 0 1 0 8 0v-.2M6.5 11.5h11M9.4 13.3h5.2" />
  </svg>
);

export const IconFolder = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <path d="M3 6.5A1.5 1.5 0 0 1 4.5 5h5l2 2.4h8A1.5 1.5 0 0 1 21 8.9v8.6a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 17.5v-11Z" />
  </svg>
);

export const IconHealth = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <path d="M3 12h4l2.2-5 3 9.4 2.3-4.4H21" />
  </svg>
);

export const IconHome = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <path d="m3.8 10.4 8.2-7 8.2 7V19a1.6 1.6 0 0 1-1.6 1.6h-3.2v-5.2a1.2 1.2 0 0 0-1.2-1.2h-4.4a1.2 1.2 0 0 0-1.2 1.2v5.2H5.4A1.6 1.6 0 0 1 3.8 19v-8.6Z" />
  </svg>
);

export const IconSpark = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <path d="M12 2.8l1.9 5.4 5.3 1.9-5.3 1.9L12 17.4l-1.9-5.4-5.3-1.9 5.3-1.9L12 2.8Z" />
    <path d="M19 16.6l.8 2.1 2.1.8-2.1.8-.8 2.1-.8-2.1-2.1-.8 2.1-.8.8-2.1Z" />
  </svg>
);

export const IconBolt = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <path d="M13.2 2.5 4.6 13.4h5.2l-1 8.1 8.6-10.9h-5.2l1-8.1Z" />
  </svg>
);

export const IconLock = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <rect x="4.5" y="10.5" width="15" height="9.5" rx="2" />
    <path d="M8 10.5V7.6a4 4 0 0 1 8 0v2.9M12 14.6v2.2" />
  </svg>
);

export const IconClock = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" {...base} aria-hidden="true">
    <circle cx="12" cy="12" r="8.8" />
    <path d="M12 6.8V12l3.4 2.4" />
  </svg>
);
