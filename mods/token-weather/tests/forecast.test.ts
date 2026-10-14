import { expect, test } from 'claude-code/testing'

const WINDOW = 200_000
const BAND = { component: 'AbovePrompt', props: { hasSurvey: false, isWorking: false, maxRows: 10 } } as const

function turn(n: number) {
  return { answer: 'ok', durationMs: 1, isAborted: false, turnId: `t${n}`, reason: 'answer' } as const
}

test('band shows weather, usage, chart and last-turn growth', async ($, on) => {
  let tokens = 36_100
  on('session.usage', () => ({ value: { startedAt: 0, rateLimits: [], context: { tokens, window: WINDOW, percent: Math.round((tokens / WINDOW) * 100) } } }))
  on('turn.complete', (_$, e) => ({ text: e.answer }))

  await $.turn.complete(turn(1))
  tokens = 134_400
  await $.turn.complete(turn(2))

  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ plugin: 'token-weather', surface, ...BAND } as never)
    expect(await ui.find({ type: 'Text', text: /☂ Showers/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /67% · 134\.4k \/ 200k/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /^\s*▂▆$/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /▲ \+98\.3k last turn/ })).toBeDefined()
    await ui.unmount()
  }
})

test('keeps only the last 12 turns and ignores subagents', async ($, on) => {
  let tokens = 0
  on('session.usage', () => ({ value: { startedAt: 0, rateLimits: [], context: { tokens, window: WINDOW } } }))
  on('turn.complete', (_$, e) => ({ text: e.answer }))

  for (let i = 1; i <= 15; i++) {
    tokens = i * 12_000
    await $.turn.complete(turn(i))
  }
  tokens = 999
  await $.turn.complete({ ...turn(99), agentId: 'sub' })

  const ui = await $.ui.mount({ plugin: 'token-weather', surface: 'terminal', ...BAND } as never)
  const chart = (await ui.find({ type: 'Text', text: /^\s*[▁▂▃▄▅▆▇█]+$/ }))?.text.trim() ?? ''
  expect([...chart].length).toBe(12)
  expect(await ui.find({ type: 'Text', text: /↯ Compact soon/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /90% · 180k \/ 200k/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /▲ \+12k last turn/ })).toBeDefined()
})
