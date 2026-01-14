import defaultsDeep from 'lodash/defaultsDeep'
export const defaultMenuConfig = {
  label: {
    text: ''
  },
  icons: {
    css: 'fa fa-ellipsis-h'
  },
  dataSource: null,
  selection: {
    // option ({label, value})
    options: [
      {
        label: 'Template Settings',
        icon: 'fa fa-cog',
        value: 'template_settings',
        type: 'item',
        variant: 'secondary'
      },
      {
        label: 'Save',
        icon: 'fa fa-floppy-o',
        value: 'save_widget',
        type: 'item',
        variant: 'primary'
      },
      {
        label: 'Save As',
        icon: 'fa fa-clone',
        value: 'save_as_widget',
        type: 'item',
        variant: 'primary'
      },
      {
        label: 'Remove',
        icon: 'fa fa-times',
        value: 'remove_template',
        type: 'item',
        variant: 'danger'
      }
    ]
  }
}

export const makeMenuDefaultConfig = (configObj) => {
  defaultsDeep(configObj, defaultMenuConfig)
}
