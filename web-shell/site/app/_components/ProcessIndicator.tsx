'use client';

import { useEffect } from 'react';

export default function ProcessIndicator({
  active,
  label = 'CareerHub is working…',
  detail,
}: {
  active: boolean;
  label?: string;
  detail?: string;
}) {
  useEffect(() => {
    if (!active) return;
    const original = document.title;
    let on = true;
    const timer = window.setInterval(() => {
      document.title = on ? `● ${original}` : original;
      on = !on;
    }, 700);
    return () => {
      window.clearInterval(timer);
      document.title = original;
    };
  }, [active]);

  if (!active) return null;

  return (
    <div className="process-indicator" role="status" aria-live="polite">
      <span className="process-indicator__dot" aria-hidden="true" />
      <span>
        <strong>{label}</strong>
        {detail ? <span className="process-indicator__detail">{detail}</span> : null}
      </span>
    </div>
  );
}
