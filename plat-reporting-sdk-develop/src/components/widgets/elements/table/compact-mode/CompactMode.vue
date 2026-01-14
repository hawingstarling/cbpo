<template>
  <div class="cbpo-compact-mode">
    <slot :toggleCompactMode="toggleCompactMode" :inCompactMode="inCompactMode" name="button">
      <b-button
        class="compact-mode-controller"
        :variant="inCompactMode ? 'secondary' : 'outline-secondary'"
        text="Compact"
        size="sm"
        @click="toggleCompactMode()"
        title="Compact Mode Toggler"
      >
        <i class="fa fa-crosshairs"></i>
      </b-button>
    </slot>
  </div>
</template>

<script>
import CBPO from '@/services/CBPO'
import { BUS_EVENT } from '@/services/eventBusType'
import { COMPACT_MODE } from '@/components/widgets/elements/table/TableConfig'

export default {
  name: 'CompactMode',
  props: {
    configObj: Object
  },
  data() {
    return {
      bodyElement: document.body
    }
  },
  computed: {
    inCompactMode() {
      return this.configObj.mode === COMPACT_MODE.HIGH
    }
  },
  methods: {
    async toggleCompactMode() {
      if (this.configObj.mode === COMPACT_MODE.HIGH) {
        this.configObj.mode = COMPACT_MODE.NORMAL
      } else if (this.configObj.mode === COMPACT_MODE.NORMAL) {
        this.configObj.mode = COMPACT_MODE.HIGH
      }
      CBPO.$bus.$emit(BUS_EVENT.COMPACT_MODE_TRIGGER, this.configObj.mode)
    }
  }
}
</script>

<style lang="scss">
.compact-mode-controller {
  font-size: 12px;
}

// Compact Mode
.cbpo-compact-mode-high {
  $compactCellHeight: 20px;
  @mixin spacing-y($property, $value) {
    #{$property}-top: $value !important;
    #{$property}-bottom: $value !important;
  }

  &.cbpo-table-element-container {
    .cbpo-progress-container {
      width: 100%;
      height: 20px;
      margin-top: 5.5px;

      .cbpo-progress {
        height: 16.5px;
        border-radius: 3px;
      }
    }

    .bulk-event-mode-content {
      margin-top: 0!important;
      padding: .125rem!important;
    }

    .cbpo-screen-cover {
      // Functional heading
      .cbpo-table-action {
        padding: 0 !important;
        min-height: 26px;

        button.btn {
          line-height: 0.75;
          padding: 0.2rem 0.25rem;
        }

        .action-buttons,
        .cbpo-timezone-selector,
        .cbpo-compact-mode {
          display: flex;
          align-items: center;
        }

        .action-checkbox ~ span {
          padding-top: 1px;
        }
      }

      .cbpo-table-global-grouping {
        display: flex;
        align-items: center;
        padding: 0 !important;
        @include spacing-y(margin, 0);

        label {
          font-size: 12px;
          padding-top: 1px;
        }
      }

      .summaries {
        .left-side,
        .right-side {
          height: 12px;
          line-height: 12px;
        }

        .custom-p {
          @include spacing-y(padding, 0);
        }
      }

      .cbpo-widget-menu {
        @include spacing-y(margin, auto);

        .dropdown-toggle {
          padding: 0 5px;
        }
      }

      // Tabel cell && height
      .cbpo-table {
        .cbpo-table-header,
        .cbpo-table-footer {
          & + .cbpo-table-header {
            top: $compactCellHeight;
          }

          .cbpo-header-col {
            height: $compactCellHeight;
            line-height: $compactCellHeight;
            min-height: $compactCellHeight;
            @include spacing-y(padding, 0);
          }

          &.cbpo-header-multi-line {
            .cbpo-header-col {
              height: auto;
              line-height: normal;
            }

            .cbpo-aggr-options {
              margin-bottom: 4px !important;
            }

            .tbl-col-header {
              margin: 0 4px;

              .cbpo-grouping-setup-icon {
                margin-right: 4px;
              }

              .sorting-holder {
                margin-left: 4px;
              }
            }
          }
          &.cbpo-table-summary {
            .tbl-col-header {
              margin: 0 4px;
            }
          }
        }

        .cbpo-table-body {
          .cbpo-table-cell {
            height: $compactCellHeight;
            line-height: $compactCellHeight;
            min-height: $compactCellHeight;
            @include spacing-y(padding, 0);

            .tbl-col-header,
            .tbl-cell-body {
              margin: 0 4px;
              height: 100%;
            }

            .text {
              height: 100%;
              line-height: calc(#{$compactCellHeight} - 1px);
            }

            .cbpo-cell--for-cursor {
              &:before {
                height: calc(#{$compactCellHeight} - 1px);
              }
            }
          }
        }

        // Action button
        .action-checkbox {
          height: $compactCellHeight;
          background-size: calc(#{$compactCellHeight} - 4px);
        }

        .action-buttons .btn-sm {
          line-height: 0.75;
          padding: 0.1rem 0.2rem;
        }
      }
    }
  }
}
</style>
