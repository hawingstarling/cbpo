import formatDirective from '@/directives/formatDirective'
import connectorDirective from '@/directives/connectorDirective'
import dragDirective from '@/directives/dragDirective'
import dropDirective from '@/directives/dropDirective'
import zIndexDirective from '@/directives/zIndexDirective'
import loadingDirective from '@/directives/loadingDirective'

export default {
  'cbpo-format': formatDirective,
  'cbpo-draggable': dragDirective,
  'cbpo-droppable': dropDirective,
  'cbpo-connector': connectorDirective,
  'cbpo-z-index': zIndexDirective,
  'cbpo-loading': loadingDirective
}
