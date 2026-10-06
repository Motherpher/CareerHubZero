'use client';

import { useEffect, useState } from 'react';
import ProcessIndicator from './ProcessIndicator';

type MotorStatus = 'idle' | 'locating' | 'queued' | 'in_progress' | 'completed' | 'not_found' | 'unconfigured' | 'unknown';

export default function MotorRunIndicator({ actionId }: { actionId: string }) {
  const [status, setStatus] = useState<MotorStatus>(actionId ? 'locating' : 'idle');
  const [conclusion, setConclusion] = useState('');

  useEffect(() => {
    if (!actionId) {
      setStatus('idle');
      setConclusion('');
      return;
    }

    let cancelled = false;
    let misses = 0;
    setStatus('locating');
    setConclusion('');

    async function check() {
      try {
        const response = await fetch(`/api/action?action_id=${encodeURIComponent(actionId)}`, { cache: 'no-store' });
        const data = await response.json().catch(() => ({}));
        if (cancelled) return;
        if (!response.ok) {
          misses += 1;
          if (misses > 12) setStatus('unknown');
          return;
        }
        const next = String(data.status ?? 'locating') as MotorStatus;
        if (next === 'not_found') {
          misses += 1;
          if (misses > 12) setStatus('unknown');
          else setStatus('locating');
          return;
        }
        misses = 0;
        setStatus(next);
        setConclusion(String(data.conclusion ?? ''));
      } catch {
        misses += 1;
        if (!cancelled && misses > 12) setStatus('unknown');
      }
    }

    void check();
    const timer = window.setInterval(() => void check(), 3000);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [actionId]);

  const active = status === 'locating' || status === 'queued' || status === 'in_progress';
  if (active) {
    const label = status === 'locating' ? 'Connecting to the active motor run…' : status === 'queued' ? 'CareerHub motor is waiting to start…' : 'CareerHub motor is working…';
    const detail = status === 'in_progress' ? 'The governed operation is running in the background. You can keep using CareerHub.' : 'CareerHub is following this request until the motor starts.';
    return <ProcessIndicator active label={label} detail={detail} />;
  }

  if (status === 'completed' && conclusion && conclusion !== 'success') {
    return <div className="process-result process-result--error" role="alert"><strong>Motor run finished with {conclusion}.</strong><span>Use reference {actionId} if you need to trace the run.</span></div>;
  }

  if (status === 'unknown') {
    return <div className="process-result" role="status"><strong>Motor status could not be confirmed.</strong><span>The request reference is {actionId}. Refresh this page or check again later.</span></div>;
  }

  return null;
}
