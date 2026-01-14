<template>
  <span v-if="!summary.tooltip" class="d-inline-block custom-p" :class="{'custom-boder': hasSeparator}">
    <strong>{{ summary.label }}:</strong>
    <span v-if="summary.defaultValue" class="pl-1">{{ summary.defaultValue }}</span>
    <span v-else class="pl-1" v-html="parsingContent"></span>
  </span>
  <span v-else class="d-inline-flex custom-p">
    <strong>{{ summary.label }}:</strong>
    <div id="question-tooltip" v-html="summary.tooltip.trigger" class="pl-1">
    </div>
    <b-popover custom-class="custom-tooltip" target="question-tooltip" triggers="hover" :placement="summary.tooltip.position">
      <div v-html="summary.tooltip.content"></div>
    </b-popover>
  </span>
</template>

<script>
import expressionParser from '@/services/ds/expression/ExpressionParser'
import { SHORT_CODES } from '@/utils/exprUtils'
import get from 'lodash/get'
import cloneDeep from 'lodash/cloneDeep'
import groupBy from 'lodash/groupBy'
import { BUS_EVENT } from '@/services/eventBusType'
import CBPO from '@/services/CBPO'

export default {
  name: 'Summary',
  props: {
    summary: {
      type: Object,
      default: () => {}
    },
    config: {
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
  computed: {
    hasSeparator () {
      const clonedSummaries = cloneDeep(this.config.globalSummary.summaries)
      const groupedList = groupBy(clonedSummaries, 'position')
      const summeriesData = {...groupedList}
      if (this.summary.position === 'left') {
        const sumIndex = summeriesData.left.findIndex(sum => sum.id === this.summary.id)
        if (sumIndex === summeriesData.left.length - 1) return false
        else return true
      } else {
        const sumIndex = summeriesData.right.findIndex(sum => sum.id === this.summary.id)
        if (sumIndex === summeriesData.right.length - 1) return false
        else return true
      }
    }
  },
  methods: {
    async eval () {
      const expressions = [{
        name: SHORT_CODES.FORMAT,
        attributes: {
          format: get(this.summary, 'format', ''),
          type: get(this.summary, 'type', ''), // optional, for format is format string
          expression: get(this.summary, 'expr', ''),
          prefix: get(this.summary, 'prefix', ''),
          suffix: get(this.summary, 'suffix', '')
        },
        content: this.summary.expr || '',
        shortCode: this.summary.expr || ''
      }]
      const evalData = await this.expressionParser.eval(expressions, this.config)
      const { parsingContent } = this.expressionParser.replaceShortcodeContent(evalData, get(this.summary, 'expr', ''))
      // remove text before Error or No data
      const errRegex = /<span(\s+)?(style\s*=\s*"([^"]*)")?>#Error<\/span>/gi
      const noDataRegex = /<span(\s+)?(style\s*=\s*"([^"]*)")?>#No data<\/span>/gi
      this.parsingContent = parsingContent
        .replace(errRegex, '<span class="text-danger">Error</span>')
        .replace(noDataRegex, this.summary.noDataMessage)
    }
  },
  async created () {
    if (get(this.summary, 'expr')) {
      await this.eval()
    }
    CBPO.$bus.$on(BUS_EVENT.SINGLE_DELETE(this.config.id), async (id) => {
      await this.eval()
    })
    CBPO.$bus.$on(BUS_EVENT.BULK_DELETE(this.config.id), async (id) => {
      await this.eval()
    })
  },
  watch: {
    'config.filter': {
      deep: true,
      async handler (val) {
        if (get(this.summary, 'expr')) {
          await this.eval()
        }
      }
    },
    'config.timezone': {
      deep: true,
      async handler (val) {
        if (get(this.summary, 'expr')) {
          await this.eval()
        }
      }
    }
  }
}
</script>

<style lang="scss" scoped>
  .custom-boder {
    position: relative;
  }
  .custom-boder::after {
    content: "/";
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    font-weight: bold;
  }
  .custom-p {
    padding: .15rem .5rem;
  }
</style>
