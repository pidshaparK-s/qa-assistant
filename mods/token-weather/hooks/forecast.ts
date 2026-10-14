import type { Sample } from '../types'

export const HISTORY = 12
const BARS = '▁▂▃▄▅▆▇█'

export type Weather = { icon: string; word: string; color: string }

export function weather(percent: number): Weather {
  if (percent < 25) return { icon: '☀', word: 'Clear', color: 'yellow' }
  if (percent < 50) return { icon: '☁', word: 'Cloudy', color: 'cyan' }
  if (percent < 75) return { icon: '☂', word: 'Showers', color: 'blue' }
  if (percent < 90) return { icon: '☇', word: 'Storm', color: 'magenta' }
  return { icon: '↯', word: 'Compact soon', color: 'red' }
}

export function compact(n: number): string {
  if (n >= 1_000_000) return `${trim(n / 1_000_000)}M`
  if (n >= 1_000) return `${trim(n / 1_000)}k`
  return String(n)
}

function trim(x: number): string {
  return x.toFixed(1).replace(/\.0$/, '')
}

// Each bar is scaled against the window, so a full bar means a full context.
export function sparkline(history: readonly Sample[]): string {
  return history
    .map(s => {
      const ratio = s.window > 0 ? Math.min(1, s.tokens / s.window) : 0
      return BARS[Math.min(BARS.length - 1, Math.floor(ratio * BARS.length))]
    })
    .join('')
}

export function delta(history: readonly Sample[]): string | undefined {
  const last = history[history.length - 1]
  const prev = history[history.length - 2]
  if (!last || !prev) return undefined
  const d = last.tokens - prev.tokens
  if (d >= 0) return `▲ +${compact(d)} last turn`
  return `▼ −${compact(-d)} last turn`
}
