<template>
  <div class="text text-truncate" v-if="column.summary">
    <span v-if="column.summary.label">{{ column.summary.label }}: </span>
    <span v-if="parsingContent" v-html="parsingContent" ></span>
  </div>
</template>

<script>
import expressionParser from '@/services/ds/expression/ExpressionParser'
import { SHORT_CODES } from '@/utils/exprUtils'
import get from 'lodash/get'

export default {
  name: 'Summary',
  props: {
    config: {
      type: Object,
      default: () => {}
    },
    column: {
      type: Object,
      default: () => {}
    }
  },
  data () {
    return {
      expressionParser,
      parsingContent: ''
    }
  },
  methods: {
    async eval () {
      const expressions = [{
        name: SHORT_CODES.FORMAT,
        attributes: {
          format: get(this.column.summary, 'format', ''),
          type: get(this.column.summary, 'type', ''), // optional, for format is format string
          expression: get(this.column.summary, 'expr', ''),
          prefix: get(this.column.summary, 'prefix', ''),
          suffix: get(this.column.summary, 'suffix', ''),
          style: get(this.column.summary, 'style', '')
        },
        content: this.column.summary.expr || '',
        shortCode: this.column.summary.expr || ''
      }]
      const evalData = await this.expressionParser.eval(expressions, this.config)
      const { parsingContent } = this.expressionParser.replaceShortcodeContent(evalData, get(this.column.summary, 'expr', ''))
      // remove text before Error or No data
      const errRegex = /<span(\s+)?(style\s*=\s*"([^"]*)")?>#Error<\/span>/gi
      const noDataRegex = /<span(\s+)?(style\s*=\s*"([^"]*)")?>#No data<\/span>/gi
      this.parsingContent = parsingContent
        .replace(errRegex, '<span class="text-danger">Error</span>')
        .replace(noDataRegex, this.column.summary.noDataMessage)
    }
  },
  async created () {
    if (get(this.column.summary, 'expr')) {
      await this.eval()
    }
  },
  watch: {
    'config.filter': {
      deep: true,
      async handler (val) {
        if (get(this.column.summary, 'expr')) {
          await this.eval()
        }
      }
    }
  }
}
</script>

<style lang="scss" scoped>
  .text {
    font-weight: bold;
  }
</style>
