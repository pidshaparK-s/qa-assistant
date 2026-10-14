export type Sample = { tokens: number; window: number }

declare module 'claude-code' {
  interface PluginState {
    'token-weather': { history: Sample[] }
  }
}
