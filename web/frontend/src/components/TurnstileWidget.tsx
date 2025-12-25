'use client';

import { useEffect, useRef } from 'react';

interface TurnstileWidgetProps {
  siteKey: string;
  onVerify: (token: string) => void;
  onError?: (error: string) => void;
  theme?: 'light' | 'dark' | 'auto';
}

/**
 * Cloudflare Turnstile Widget Component
 * 
 * Embeds the Turnstile CAPTCHA and handles verification callbacks
 */
export default function TurnstileWidget({
  siteKey,
  onVerify,
  onError,
  theme = 'auto',
}: TurnstileWidgetProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const widgetIdRef = useRef<string | null>(null);

  useEffect(() => {
    // Check if Turnstile script is already loaded
    const existingScript = document.querySelector('script[src="https://challenges.cloudflare.com/turnstile/v0/api.js"]');
    
    const renderWidget = () => {
      if (containerRef.current && window.turnstile && !widgetIdRef.current) {
        // Render Turnstile widget
        widgetIdRef.current = window.turnstile.render(containerRef.current, {
          sitekey: siteKey,
          theme,
          callback: (token: string) => {
            onVerify(token);
          },
          'error-callback': () => {
            onError?.('Turnstile verification failed');
          },
          'expired-callback': () => {
            onError?.('Turnstile token expired');
          },
        });
      }
    };

    if (existingScript) {
      // Script already loaded, just render the widget
      if (window.turnstile) {
        renderWidget();
      } else {
        // Script tag exists but not loaded yet, wait for it
        existingScript.addEventListener('load', renderWidget);
      }
    } else {
      // Load Turnstile script for the first time
      const script = document.createElement('script');
      script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js';
      script.async = true;
      script.defer = true;
      script.onload = renderWidget;
      document.head.appendChild(script);
    }

    return () => {
      // Cleanup: remove widget on unmount
      if (widgetIdRef.current && window.turnstile) {
        window.turnstile.remove(widgetIdRef.current);
        widgetIdRef.current = null;
      }
    };
  }, [siteKey, theme, onVerify, onError]);

  return (
    <div
      ref={containerRef}
      className="flex justify-center items-center my-4"
      aria-label="Cloudflare Turnstile verification"
    />
  );
}

// Type definitions for Turnstile global
declare global {
  interface Window {
    turnstile?: {
      render: (
        container: HTMLElement,
        options: {
          sitekey: string;
          theme?: 'light' | 'dark' | 'auto';
          callback?: (token: string) => void;
          'error-callback'?: () => void;
          'expired-callback'?: () => void;
        }
      ) => string;
      remove: (widgetId: string) => void;
      reset: (widgetId: string) => void;
    };
  }
}
