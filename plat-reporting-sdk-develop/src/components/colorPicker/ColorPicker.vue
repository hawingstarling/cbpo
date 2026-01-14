<template>
  <div v-on-clickaway="awayPicker" class="input-group color-picker">
    <input type="text" class="form-control" v-model="colorValue" @focus="displayPicker=true" @input="updateFromInput" />
    <span class="input-group-addon color-picker-container">
      <span class="current-color" :style="`background-color: ${colorValue}`" @click="togglePicker()"></span>
      <sketch-picker :value="colors" @input="updateFromPicker" v-if="displayPicker" />
    </span>
  </div>
</template>
<script>
import { Sketch } from 'vue-color'
import { mixin as clickaway } from 'vue-clickaway'

export default {
  name: 'ColorPicker',
  props: {
    color: String,
    defaultColor: {
      type: String,
      default: ''
    }
  },
  mixins: [clickaway],
  components: {
    'sketch-picker': Sketch
  },
  data() {
    return {
      colors: {
        hex: this.defaultColor
      },
      colorValue: '',
      displayPicker: false
    }
  },
  mounted() {
    this.setColor(this.color || this.defaultColor)
  },
  methods: {
    togglePicker() {
      this.displayPicker = !this.displayPicker
    },
    setColor(color) {
      this.updateColors(color)
      this.colorValue = color
    },
    updateColors(color) {
      if (color) {
        if (color.slice(0, 1) === '#') {
          this.colors = {
            hex: color
          }
        } else if (color.slice(0, 4) === 'rgba') {
          let rgba = color.replace(/^rgba?\(|\s+|\)$/g, '').split(',')
          let hex = '#' + ((1 << 24) + (parseInt(rgba[0]) << 16) + (parseInt(rgba[1]) << 8) + parseInt(rgba[2])).toString(16).slice(1)
          this.colors = {
            hex: hex,
            a: rgba[3]
          }
        }
      } else {
        this.colors = {
          hex: ''
        }
      }
    },
    updateFromInput() {
      this.updateColors(this.colorValue)
    },
    updateFromPicker(color) {
      this.colors = color
      if (color.rgba.a === 1) {
        this.colorValue = color.hex
      } else {
        this.colorValue = `rgba(${color.rgba.r}, ${color.rgba.g}, ${color.rgba.b}, ${color.rgba.a})`
      }
    },
    awayPicker() {
      this.displayPicker = false
    }
  },
  watch: {
    colorValue(val) {
      this.updateColors(val)
      this.$emit('input', val)
    }
  }
}
</script>
<style lang="scss" scoped>
  @import "ColorPicker";
</style>
