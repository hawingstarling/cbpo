<template>
  <b-button-group>
    <!-- <b-button :class="{'click-view': viewState === 'Small'}" variant="secondary" text="Small" size="sm" @click="defaultView()" title="Normal">
      <i class="fa fa-compress"></i>
    </b-button>
    <b-button :class="{'click-view': viewState === 'Large'}" variant="secondary" text="Small" size="sm" @click="largeView()" title="Large">
      <i class="fa fa-expand"></i>
    </b-button> -->
    <b-button id="expand-table-btn" :class="{'click-view': viewState === 'Fullscreen'}" variant="secondary" text="Small" size="sm" @click="toggleView()">
      <img src="@/assets/img/icon/fullscreen-icon.svg" alt="fullscreen-icon">
    </b-button>
    <b-tooltip custom-class="custom-btn-tooltip" target="expand-table-btn" triggers="hover"
               placement="top">
      <span v-if="viewState === 'Fullscreen'">Normal</span>
      <span v-else>Expand Table</span>
    </b-tooltip>
  </b-button-group>
</template>

<script>
import fullscreenMixins from '@/mixins/fullscreenMixins'

export default {
  name: 'ViewMode',
  props: {
    element: null
  },
  data() {
    return {
      bodyElement: document.body,
      viewState: 'Small'
    }
  },
  mixins: [fullscreenMixins],
  mounted() {
    document.addEventListener('fullscreenchange', () => {
      if (!this.isInFullscreen()) {
        if (this.viewState === 'Fullscreen') this.defaultView()
      }
    })
  },
  methods: {
    calculateTableHeight() {
      this.$emit('calculateTableHeight')
    },
    defaultView() {
      this.exitFullscreen()
      this.bodyElement.classList.remove(
        'sidebar-minimized',
        'brand-minimized',
        'larger-view-mode'
      )
      this.calculateTableHeight()
      this.viewState = 'Small'
    },
    optimizeView() {
      this.bodyElement.classList.add(
        'sidebar-minimized',
        'brand-minimized',
        'larger-view-mode'
      )
      this.calculateTableHeight()
    },
    largeView() {
      this.exitFullscreen()
      this.optimizeView()
      this.viewState = 'Large'
    },
    fullscreenView() {
      this.requestFullscreen()
      this.optimizeView()
      this.viewState = 'Fullscreen'
    },
    toggleView() {
      if (this.viewState === 'Fullscreen') {
        this.defaultView()
      } else {
        this.fullscreenView()
      }
    }
  }
}
</script>

<style lang="scss">
body.larger-view-mode {
  .app-header + .app-body {
    margin-top: 0;
    .sidebar {
      height: 100vh;
    }
    .breadcrumb {
      opacity: 0;
      visibility: hidden;
      height: 0.5rem;
      padding: 0;
      margin: 0;
      display: none;
    }
    .container-fluid{
      padding-top: 20px;
    }
    .cbpo-widget-wrapper {
      .cbpo-widget-title {
        display: none;
      }
    }
  }
  //   .app-footer {
  //     display: none;
  //   }
}
.custom-btn-tooltip {
    box-shadow: 0px 12px 16px -4px rgba(16, 24, 40, 0.08), 0px 4px 6px -2px rgba(16, 24, 40, 0.03);
    border-radius: 8px;
    .popover-body {
      color: #344054;
      font-weight: 500;
      font-size: 12px;
      line-height: 16px;
      letter-spacing: 0.01em;
    }
}
</style>
