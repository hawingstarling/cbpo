export default {
  data() {
    return {
      mixinsWidgetMenuConfig: {
        icons: {
          css: 'fa fa-ellipsis-v'
        },
        selection: {
          options: [
            {
              label: 'Export CSV',
              icon: 'fa fa-download',
              value: 'csv',
              type: 'item'
            }
          ]
        }
      }
    }
  }
}
