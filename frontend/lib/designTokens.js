// Design System Tokens - Extracted from Admin Dashboard
// This is the SINGLE SOURCE OF TRUTH for the entire application

export const colors = {
  // Primary
  primary: 'slate-900',
  primaryLight: 'slate-50',
  primaryBorder: 'slate-200',

  // Text
  text: {
    primary: 'slate-900',
    secondary: 'slate-600',
    tertiary: 'slate-400',
    light: 'slate-300',
    white: 'white',
  },

  // Status colors
  success: 'emerald',
  info: 'blue',
  warning: 'orange',
  error: 'red',

  // Accent
  accent: 'indigo',

  // Backgrounds
  bg: {
    primary: 'white',
    secondary: 'slate-50',
    tertiary: 'slate-100',
  },

  // Borders
  border: {
    light: 'slate-100',
    default: 'slate-200',
    dark: 'slate-300',
  },
};

export const spacing = {
  xs: '0.25rem',
  sm: '0.5rem',
  md: '1rem',
  lg: '1.5rem',
  xl: '2rem',
  '2xl': '2.5rem',
  '3xl': '3rem',
  '4xl': '4rem',
};

export const radius = {
  sm: 'rounded-lg',
  md: 'rounded-xl',
  lg: 'rounded-2xl',
  xl: 'rounded-3xl',
  full: 'rounded-full',
};

export const shadows = {
  none: 'shadow-none',
  sm: 'shadow-sm',
  md: 'shadow-md',
  lg: 'shadow-lg',
  xl: 'shadow-xl',
};

export const typography = {
  // Page titles
  pageTitle: 'text-2xl font-bold text-slate-900',
  pageTitleSmall: 'text-xl font-bold text-slate-900',

  // Section titles
  sectionTitle: 'text-sm font-bold text-slate-900',
  sectionTitleLarge: 'text-lg font-bold text-slate-900',

  // Labels
  label: 'text-xs font-bold text-slate-400 uppercase tracking-wider',
  labelSmall: 'text-[10px] font-bold text-slate-400 uppercase tracking-widest',

  // Body text
  body: 'text-sm text-slate-900',
  bodySmall: 'text-xs text-slate-600',
  bodySemibold: 'text-sm font-semibold text-slate-900',

  // Uppercase
  uppercase: 'uppercase',
  tracking: 'tracking-wider',
};

export const buttons = {
  // Primary Button
  primary: `px-4 py-2 bg-slate-900 text-white text-xs font-bold uppercase tracking-wider rounded-lg hover:bg-slate-800 transition-colors`,
  primaryLarge: `px-6 py-3 bg-slate-900 text-white text-sm font-bold uppercase tracking-wider rounded-lg hover:bg-slate-800 transition-colors`,

  // Secondary Button
  secondary: `px-4 py-2 bg-white border border-slate-200 text-slate-700 text-xs font-bold uppercase tracking-wider rounded-lg hover:bg-slate-50 transition-colors`,
  secondaryLarge: `px-6 py-3 bg-white border border-slate-200 text-slate-700 text-sm font-bold uppercase tracking-wider rounded-lg hover:bg-slate-50 transition-colors`,

  // Ghost Button
  ghost: `px-4 py-2 text-slate-600 hover:bg-slate-50 rounded-lg transition-colors text-xs font-semibold`,

  // Pill Button (for categories/filters)
  pill: `px-6 py-2 rounded-full text-xs font-bold uppercase tracking-wider transition-all duration-300`,
  pillActive: `px-6 py-2 rounded-full text-xs font-bold uppercase tracking-wider transition-all duration-300 bg-slate-900 text-white shadow-md`,
  pillInactive: `px-6 py-2 rounded-full text-xs font-bold uppercase tracking-wider transition-all duration-300 bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 shadow-sm`,
};

export const inputs = {
  base: `w-full bg-slate-50 border border-slate-200 rounded-lg py-2 px-3 text-sm outline-none focus:border-slate-400 focus:bg-white transition-all`,
  large: `w-full bg-slate-50 border border-slate-200 rounded-lg py-3 px-4 text-sm outline-none focus:border-slate-400 focus:bg-white transition-all`,
  search: `w-full bg-slate-50 border border-slate-200 rounded-lg py-2 pl-9 pr-3 text-sm outline-none focus:border-slate-400 focus:bg-white transition-all`,
};

export const cards = {
  base: `bg-white border border-slate-200 rounded-xl`,
  elevated: `bg-white border border-slate-200 rounded-xl shadow-sm hover:shadow-md transition-shadow`,
  padding: `p-5`,
  paddingLarge: `p-6`,
};

export const badges = {
  success: `bg-emerald-50 text-emerald-700 border-emerald-200 text-xs font-semibold rounded-lg px-2.5 py-1.5`,
  info: `bg-blue-50 text-blue-700 border-blue-200 text-xs font-semibold rounded-lg px-2.5 py-1.5`,
  warning: `bg-orange-50 text-orange-700 border-orange-200 text-xs font-semibold rounded-lg px-2.5 py-1.5`,
  error: `bg-red-50 text-red-700 border-red-200 text-xs font-semibold rounded-lg px-2.5 py-1.5`,
  neutral: `bg-slate-50 text-slate-600 border-slate-200 text-xs font-semibold rounded-lg px-2.5 py-1.5`,
};

export const layouts = {
  container: `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`,
  containerSmall: `max-w-5xl mx-auto px-4 sm:px-6`,
  containerLarge: `max-w-7xl mx-auto px-4`,

  // Main page layout
  pageLayout: `min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900`,
  mainContent: `flex-grow w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10`,

  // Grid layouts
  gridAuto: `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6`,
  grid2Col: `grid grid-cols-1 md:grid-cols-2 gap-6`,
  grid3Col: `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6`,
  grid4Col: `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6`,
};

export const states = {
  // Status badges for orders
  statusPending: `bg-orange-50 text-orange-700 border-orange-200`,
  statusProcessing: `bg-indigo-50 text-indigo-700 border-indigo-200`,
  statusShipped: `bg-blue-50 text-blue-700 border-blue-200`,
  statusDelivered: `bg-emerald-50 text-emerald-700 border-emerald-200`,
  statusCancelled: `bg-red-50 text-red-700 border-red-200`,
};

// Utility function to build responsive classes
export const responsive = {
  mobileFirst: (mobile, tablet, desktop) => `${mobile} sm:${tablet} lg:${desktop}`,
};
