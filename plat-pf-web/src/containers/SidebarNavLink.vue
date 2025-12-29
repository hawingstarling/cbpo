<template>
  <router-link :to="to ? to : url" :class="classList" v-bind="attributes" v-if="image">
    <img :src="require(`./../assets/img/${image}`)" :style="imageStyle" class="nav-image"> <span>{{name}}</span>
    <b-badge v-if="badge && badge.text" :variant="badge.variant">{{badge.text}}</b-badge>
  </router-link>
  <a :class="classList" v-bind="attributes" tabindex="-1" v-on:click.stop.prevent v-else-if="isDisabled">
    <i :class="classIcon"></i> <span>{{name}}</span>
    <b-badge v-if="badge && badge.text" :variant="badge.variant">{{badge.text}}</b-badge>
  </a>
  <a :href="url" :class="classList" v-bind="attributes" v-else-if="isExternalLink">
    <i :class="classIcon"></i> {{name}}
    <b-badge v-if="badge && badge.text" :variant="badge.variant">{{badge.text}}</b-badge>
  </a>
  <router-link :to="to ? to : url" :class="classList" v-bind="attributes" v-else>
    <i :class="classIcon"></i> {{name}}
    <b-badge v-if="badge && badge.text" :variant="badge.variant">{{badge.text}}</b-badge>
  </router-link>
</template>

<script>
export default {
  name: 'sidebar-nav-link',
  props: {
    name: {
      type: String,
      default: ''
    },
    url: {
      type: String,
      default: ''
    },
    to: {
      type: Object,
      default: () => {}
    },
    icon: {
      type: String,
      default: ''
    },
    badge: {
      type: Object,
      default: () => {}
    },
    variant: {
      type: String,
      default: ''
    },
    classes: {
      type: [String, Array, Object],
      default: ''
    },
    attributes: {
      type: Object,
      default: () => { return Object.create(null) }
    },
    image: {
      type: String,
      default: ''
    },
    imageStyle: {
      type: Object,
      default: () => { return Object.create(null) }
    }
  },
  computed: {
    classList () {
      return [
        'nav-link',
        this.linkVariant,
        ...this.disabledClasses,
        ...this.attrClasses,
        ...this.itemClasses,
        ...this.activeClasses
      ]
    },
    classIcon () {
      return [
        'nav-icon',
        this.icon
      ]
    },
    linkVariant () {
      return this.variant ? `nav-link-${this.variant}` : ''
    },
    itemClasses () {
      return this.getClassArray(this.classes)
    },
    attrClasses () {
      return this.getClassArray(this.attributes.class)
    },
    disabledClasses () {
      return this.isDisabled ? 'disabled'.split(' ') : []
    },
    activeClasses () {
      // Check if current route is a child of the target route
      if (this.to && this.to.name && this.$route.matched && this.$route.matched.length > 0) {
        const isChildRoute = this.$route.matched.some(route => route.name === this.to.name)
        return isChildRoute ? ['router-link-active'] : []
      }
      return []
    },
    isDisabled () {
      return Boolean(this.attributes.disabled)
    },
    isExternalLink () {
      return Boolean(this.url.substring(0, 4) === 'http')
    }
  },
  methods: {
    getClassArray(classes) {
      /* eslint-disable */
      return !classes ? [] : typeof classes === 'string' || classes instanceof String ? classes.split(' ') : Array.isArray(classes) ? classes : Object.keys(classes).filter(i=>classes[i])
    }
  }
}
</script>
