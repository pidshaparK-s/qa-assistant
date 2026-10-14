import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Sample } from '../types'
import { HISTORY, compact, delta, sparkline, weather } from './forecast'

const history = atom({ plugin: 'token-weather', key: 'history' } as const, [] as Sample[])

export const register: Register = on => {
  on('turn.complete', async ($, e, next) => {
    const result = await next(e)
    if (e.agentId !== undefined) return result

    const { context } = await $.session.usage()
    if (context.tokens !== undefined && context.window > 0) {
      const sample: Sample = { tokens: context.tokens, window: context.window }
      await update($, history, past => [...past, sample].slice(-HISTORY))
    }

    return result
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const samples = await read($, history)
    const last = samples[samples.length - 1]
    if (e.props.hasSurvey || !last) return next(e)

    const { Box, Text } = $.ui.resolve(e)
    const percent = Math.round((last.tokens / last.window) * 100)
    const w = weather(percent)
    const change = delta(samples)

    return (
      <Box flexDirection="row">
        <Text color={w.color} weight="bold">
          {w.icon} {w.word}
        </Text>
        <Text>
          {'  '}
          {percent}% · {compact(last.tokens)} / {compact(last.window)}
        </Text>
        <Text color={w.color}>
          {'  '}
          {sparkline(samples)}
        </Text>
        {change ? (
          <Text dimColor>
            {'  '}
            {change}
          </Text>
        ) : null}
      </Box>
    )
  })
}
