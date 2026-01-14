import _ from 'lodash'
import { DEFAULT_PAGINATION_CONFIG } from '@/components/widgets/elements/table/pagination/PaginationConfig'
import { defaultTimezone } from '@/utils/timezoneUtil'

export const defaultHtmlEditorConfig = {
  builder: { enabled: false },
  content: ``,
  pagination: Object.assign({}, DEFAULT_PAGINATION_CONFIG),
  sorting: [],
  columns: [],
  grouping: {
    columns: [],
    aggregations: []
  },
  bins: [],
  timezone: {
    enabled: false,
    utc: null, // String value from moment().tz.names() list | abbr. maybe not accurate in some cases
    /* https://github.com/dmfilipenko/timezones.json */
    visible: true // show timezone select box
  },
  options: {
    plugins: [
      'advlist autolink lists link image preview anchor',
      'searchreplace visualblocks code',
      'insertdatetime media table paste'
    ],
    toolbar: 'undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft aligncenter alignright alignjustify | outdent indent |  numlist bullist checklist | forecolor backcolor casechange permanentpen formatpainter removeformat | pagebreak | charmap emoticons | fullscreen  preview save print | insertfile image media pageembed template link anchor codesample | a11ycheck ltr rtl | showcomments addcomment'
  },
  sizeSettings: {
    defaultMinSize: 250,
    warningText: 'The area is too small for this visualization.'
  },
  exportConfig: {
    polling: true, // false mean export is triggered and response is returned immediately in a single request
    pollingInterval: 2000 // interval between successive polling requests (in ms)
    // Note: Use polling=true for large exports that may take time to process
    // Use polling=false for small exports where immediate response is expected
  }
}

export const makeDefaultHtmlEditorConfig = (htmlEditorConfig) => {
  _.defaultsDeep(htmlEditorConfig, defaultHtmlEditorConfig)

  // default utc
  defaultTimezone(htmlEditorConfig)
}
