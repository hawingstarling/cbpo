<template>
  <b-form @submit.prevent="submit($event)">
    <b-input-group class="common-filter">
      <b-form-input
        class="form-select-custom"
        size="sm"
        v-model.trim="dataValue"
        :placeholder="placeholder"
        :class="getClassBaseOnIgnoreState"
        @change="onChangeHandler()"
      >
      </b-form-input>
      <i
        class="fa fa-times-circle clear-keyword"
        v-if="dataValue"
        @click="clearKeyword()"
      ></i>
      <div class="search-img" @click="submit($event)">
        <img src="@/assets/img/icon/search-icon.png" alt="search-icon">
      </div>
    </b-input-group>
  </b-form>
</template>

<script>
import _ from 'lodash'

export default {
  name: 'CommonFilter',
  props: {
    value: String,
    placeholder: { type: String, default: 'Search' },
    ignoreState: Object
  },
  computed: {
    getClassBaseOnIgnoreState() {
      return this.ignoreState && this.ignoreState.base.value
        ? 'disabled-non-hover'
        : ''
    },
    dataValue: {
      get() {
        return this.$props.value || ''
      },
      set(val) {
        this.$emit('input', val)
      }
    }
  },
  methods: {
    submit(e) {
      if (!this.dataValue) {
        e.preventDefault()
        return
      }
      this.$emit('change')
    },
    clearKeyword() {
      this.dataValue = ''
      this.$emit('change')
    },
    onChangeHandler: _.debounce(function() {
      if (!this.dataValue) {
        this.$emit('change')
      }
    }, 500)
  }
}
</script>

<style lang="scss" scoped>
.common-filter {
  position: relative;
}

.form-select-custom {
  font-size: 12px;
  padding: 10px 20px 10px 40px;
  width: 100%;
  height: 36px;
  background: #FFFFFF;
  border: 1px solid #e6e8f0;
  box-shadow: 0px 1px 2px rgba(16, 24, 40, 0.05);
  border-radius: 1px;
}
.search-img {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1000;
}

.clear-keyword {
  position: absolute;
  cursor: pointer;
  right: 10px;
  top: calc(50% + 1px);
  z-index: 20;
  transform: translateY(-50%);
}

.disabled-non-hover:not(:hover) {
  background-color: #e9ecef;
  color: #6c757d;
}
</style>
