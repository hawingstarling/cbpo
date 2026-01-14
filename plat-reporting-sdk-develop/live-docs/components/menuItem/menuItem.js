const sdkMenuItem = Vue.component('sdkMenuItem', {
  template: `
    <b-nav-item-dropdown ref="dropdownMenu" v-if="routeItem.children"
                         :class="{'nav-text-dark': !root, 'dropdown-submenu': !root}"
                         :text="routeItem.name">
      <b-dropdown-item v-for="(route, index) of routeItem.children">
        <sdk-menu-item :y="index + route.name" :routeItem="route"/>
      </b-dropdown-item>
    </b-nav-item-dropdown>
    <b-nav-item target="_blank" v-else :class="{'nav-text-dark': !root}" :to="routeItem.path">
      {{routeItem.name}}
    </b-nav-item>
  `,
  props: {
    root: {
      type: Boolean,
      default: false
    },
    routeItem: Object
  }
})
