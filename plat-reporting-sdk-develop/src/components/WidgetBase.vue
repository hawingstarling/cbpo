<script>
/**
 * Implement if your callbacks is AFER child components callbacks.
 * @see https://alligator.io/vuejs/composing-components/
 */
export default {
  props: {
  },
  data () {
  },
  methods: {
    widgetInit: () => {
      console.log('WidgetBase::widgetInit')
    }
  },
  mounted () {
    console.log('WidgetBase::mounted')
  }
}
</script>
