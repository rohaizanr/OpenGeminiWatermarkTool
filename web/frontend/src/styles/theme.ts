/**
 * Material Design 3 Theme Configuration
 * 
 * Implements Material You color system with dynamic theming
 * Reference: https://m3.material.io/styles/color/the-color-system
 */

export const materialTheme = {
  colors: {
    // Primary color - Main brand color used for key components
    primary: {
      main: '#6750A4',        // Primary-40
      onPrimary: '#FFFFFF',   // On-primary
      container: '#EADDFF',   // Primary-90
      onContainer: '#21005D', // Primary-10
    },
    
    // Secondary color - Less prominent components
    secondary: {
      main: '#625B71',        // Secondary-40
      onSecondary: '#FFFFFF', // On-secondary
      container: '#E8DEF8',   // Secondary-90
      onContainer: '#1D192B', // Secondary-10
    },
    
    // Tertiary color - Contrasting accent color
    tertiary: {
      main: '#7D5260',        // Tertiary-40
      onTertiary: '#FFFFFF',  // On-tertiary
      container: '#FFD8E4',   // Tertiary-90
      onContainer: '#31111D', // Tertiary-10
    },
    
    // Error color - Validation and error states
    error: {
      main: '#B3261E',        // Error-40
      onError: '#FFFFFF',     // On-error
      container: '#F9DEDC',   // Error-90
      onContainer: '#410E0B', // Error-10
    },
    
    // Surface colors - Backgrounds and containers
    surface: {
      dim: '#DED8E1',         // Surface-dim
      main: '#FEF7FF',        // Surface
      bright: '#FEF7FF',      // Surface-bright
      containerLowest: '#FFFFFF',
      containerLow: '#F7F2FA',
      container: '#F3EDF7',
      containerHigh: '#ECE6F0',
      containerHighest: '#E6E0E9',
    },
    
    // Outline colors - Borders and dividers
    outline: {
      main: '#79747E',        // Outline
      variant: '#CAC4D0',     // Outline-variant
    },
    
    // Inverse colors - For inverse surfaces
    inverse: {
      surface: '#322F35',     // Inverse-surface
      onSurface: '#F4EFF4',   // Inverse-on-surface
      primary: '#D0BCFF',     // Inverse-primary
    },
  },
  
  // Elevation system using shadow overlays
  elevation: {
    level0: 'none',
    level1: '0px 1px 2px rgba(0, 0, 0, 0.3), 0px 1px 3px rgba(0, 0, 0, 0.15)',
    level2: '0px 1px 2px rgba(0, 0, 0, 0.3), 0px 2px 6px rgba(0, 0, 0, 0.15)',
    level3: '0px 4px 8px rgba(0, 0, 0, 0.3), 0px 1px 3px rgba(0, 0, 0, 0.15)',
    level4: '0px 6px 10px rgba(0, 0, 0, 0.3), 0px 1px 18px rgba(0, 0, 0, 0.15)',
    level5: '0px 8px 12px rgba(0, 0, 0, 0.3), 0px 4px 4px rgba(0, 0, 0, 0.15)',
  },
  
  // Typography scale
  typography: {
    display: {
      large: { fontSize: '57px', lineHeight: '64px', fontWeight: 400 },
      medium: { fontSize: '45px', lineHeight: '52px', fontWeight: 400 },
      small: { fontSize: '36px', lineHeight: '44px', fontWeight: 400 },
    },
    headline: {
      large: { fontSize: '32px', lineHeight: '40px', fontWeight: 400 },
      medium: { fontSize: '28px', lineHeight: '36px', fontWeight: 400 },
      small: { fontSize: '24px', lineHeight: '32px', fontWeight: 400 },
    },
    title: {
      large: { fontSize: '22px', lineHeight: '28px', fontWeight: 500 },
      medium: { fontSize: '16px', lineHeight: '24px', fontWeight: 500 },
      small: { fontSize: '14px', lineHeight: '20px', fontWeight: 500 },
    },
    body: {
      large: { fontSize: '16px', lineHeight: '24px', fontWeight: 400 },
      medium: { fontSize: '14px', lineHeight: '20px', fontWeight: 400 },
      small: { fontSize: '12px', lineHeight: '16px', fontWeight: 400 },
    },
    label: {
      large: { fontSize: '14px', lineHeight: '20px', fontWeight: 500 },
      medium: { fontSize: '12px', lineHeight: '16px', fontWeight: 500 },
      small: { fontSize: '11px', lineHeight: '16px', fontWeight: 500 },
    },
  },
  
  // Shape system
  shape: {
    corner: {
      none: '0px',
      extraSmall: '4px',
      small: '8px',
      medium: '12px',
      large: '16px',
      extraLarge: '28px',
      full: '9999px',
    },
  },
  
  // State layers (interaction feedback)
  states: {
    hover: 0.08,
    focus: 0.12,
    pressed: 0.12,
    dragged: 0.16,
  },
} as const;

export type MaterialTheme = typeof materialTheme;

/**
 * Get CSS variable string for a color path
 * Example: getColorVar('primary', 'main') => 'var(--md-sys-color-primary)'
 */
export function getColorVar(colorGroup: string, variant: string = 'main'): string {
  if (variant === 'main') {
    return `var(--md-sys-color-${colorGroup})`;
  }
  return `var(--md-sys-color-${colorGroup}-${variant})`;
}

/**
 * Get elevation shadow string
 */
export function getElevation(level: keyof typeof materialTheme.elevation): string {
  return materialTheme.elevation[level];
}
