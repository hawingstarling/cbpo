<template>
  <div class="cbpo-widget-title justify-content-center" :style="configStyles">
    <h4 class="mb-0 builder-on" :style="{color: configStyles.color}" v-html="loadingData.isActive ? loadingData.content : contentTitle"></h4>
  </div>
</template>
<script>
import WidgetBaseMixins from '@/components/WidgetBaseMixins'
import WidgetBase from '../../WidgetBase'
import { makeWidgetDefaultConfig } from './WidgetTitleConfig'
import expressionParser from '@/services/ds/expression/ExpressionParser'

export default {
  name: 'Title',
  extends: WidgetBase,
  mixins: [WidgetBaseMixins],
  props: {
    configStyles: {
      type: Object
    }
  },
  data () {
    return {
      contentTitle: '',
      loadingData: {
        isActive: false,
        content: '<i class="fa fa-circle-o-notch fa-spin"></i> Loading...'
      },
      expressionParser
    }
  },
  methods: {
    widgetConfig(config) {
      makeWidgetDefaultConfig(config)
      if (this.config.title.text) {
        this.parsingContentTitle(this.config.title.text)
      }
    },
    setLoaderStatus(status = false) {
      this.loadingData.isActive = status
    },
    async parsingContentTitle(title) {
      const expressions = this.expressionParser.getExpressions(title)
      if (expressions && expressions.length) {
        try {
          this.setLoaderStatus(true)
          const evalData = await this.expressionParser.eval(expressions, this.config)
          const { parsingContent } = this.expressionParser.replaceShortcodeContent(evalData, title)
          this.contentTitle = parsingContent
          this.setLoaderStatus(false)
        } catch (e) {
          this.setLoaderStatus(false)
          console.error('Error Title', e)
        }
      } else {
        this.contentTitle = title
      }
    }
  },
  watch: {
    'config.title.text'(text) {
      if (text) {
        this.parsingContentTitle(text)
      } else {
        this.contentTitle = text
      }
    }
  }
}
</script>
<style scoped lang="scss">
@import './Title.scss';
</style>
