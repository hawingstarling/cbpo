
<template>
  <nav class="sidebar-nav" @mouseover="addClassToBody(true)" @mouseleave="addClassToBody(false)">
    <VuePerfectScrollbar class="scroll-area" :settings="psSettings" @ps-scroll-y="scrollHandle">
      <ul class="nav">
        <template v-for="(item, index) in navItems">
          <template v-if="item.image">
            <li :key="index" class="nav-item">
              <SidebarNavLink :name="item.name" :url="item.url" :to="item.to" :icon="item.icon" :image="item.image" :badge="item.badge" :variant="item.variant" :attributes="item.attributes" :imageStyle="item.imageStyle" />
            </li>
          </template>
          <template v-else-if="item.title">
            <SidebarNavTitle :key="index" :name="item.name" :classes="item.class" :wrapper="item.wrapper"/>
          </template>
          <template v-else-if="item.divider">
            <SidebarNavDivider :key="index" :classes="item.class"/>
          </template>
          <template v-else-if="item.label">
            <SidebarNavLabel :key="index" :name="item.name" :url="item.url" :icon="item.icon" :label="item.label" :classes="item.class"/>
          </template>
          <template v-else>
            <template v-if="item.children">
              <!-- First level dropdown -->
              <SidebarNavDropdown :key="index" :name="item.name" :url="item.url" :icon="item.icon">
                <template v-for="(childL1, index1) in item.children">
                  <template v-if="childL1.children">
                    <!-- Second level dropdown -->
                    <SidebarNavDropdown :key="index1" :name="childL1.name" :url="childL1.url" :icon="childL1.icon">
                      <li :key="index2" class="nav-item" v-for="(childL2, index2) in childL1.children">
                        <SidebarNavLink :name="childL2.name" :url="childL2.url" :to="childL2.to" :icon="childL2.icon" :badge="childL2.badge" :variant="childL2.variant" :attributes="childL2.attributes" />
                      </li>
                    </SidebarNavDropdown>
                  </template>
                  <template v-else>
                    <SidebarNavItem :key="index1" :classes="item.class">
                      <SidebarNavLink :name="childL1.name" :url="childL1.url" :to="childL1.to" :icon="childL1.icon" :badge="childL1.badge" :variant="childL1.variant" :attributes="childL1.attributes"/>
                    </SidebarNavItem>
                  </template>
                </template>
              </SidebarNavDropdown>
            </template>
            <template v-else>
              <SidebarNavItem :key="index" :classes="item.class">
                <SidebarNavLink :name="item.name" :url="item.url" :to="item.to" :icon="item.icon" :badge="item.badge" :variant="item.variant" :attributes="item.attributes"/>
              </SidebarNavItem>
            </template>
          </template>
        </template>
      </ul>
      <slot></slot>
    </VuePerfectScrollbar>
  </nav>
</template>

<script>
import VuePerfectScrollbar from 'vue-perfect-scrollbar'
import { SidebarNavDivider, SidebarNavDropdown, SidebarNavTitle, SidebarNavItem, SidebarNavLabel } from '@coreui/vue'
import SidebarNavLink from './SidebarNavLink'

export default {
  name: 'SidebarNav',
  components: {
    SidebarNavDivider,
    SidebarNavDropdown,
    SidebarNavLink,
    SidebarNavTitle,
    SidebarNavItem,
    SidebarNavLabel,
    VuePerfectScrollbar
  },
  props: {
    navItems: {
      type: Array,
      required: true,
      default: () => []
    }
  },
  data () {
    return {}
  },
  computed: {
    psSettings: () => {
      // ToDo: find better rtl fix
      return {
        maxScrollbarLength: 200,
        minScrollbarLength: 40,
        suppressScrollX: getComputedStyle(document.querySelector('html')).direction !== 'rtl',
        wheelPropagation: false,
        interceptRailY: styles => ({ ...styles, height: 0 })
      }
    }
  },
  methods: {
  // eslint-disable-next-line
    scrollHandle (evt) {
      // console.log(evt)
    },
    addClassToBody (isHover) {
      const el = document.body
      if (isHover) {
        el.classList.add('pf-sidebar-minimized')
      } else {
        el.classList.remove('pf-sidebar-minimized')
      }
    }
  },
  mounted () {
  }
}
</script>

<style scoped lang="css">
  .scroll-area {
    position: absolute;
    height: 100%;
    margin: auto;
  }
</style>
