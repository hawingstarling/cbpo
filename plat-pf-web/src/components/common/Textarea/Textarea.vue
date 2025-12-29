<template>
  <div class="pf-textarea">
    <ValidationProvider
      :name="filteredName(name)"
      immediate
      :rules="validateRules"
      v-slot="{ errors }"
      :vid="name"
    >
      <b-form-textarea
        v-model="dataValue"
        max-rows="5"
        no-resize
        :size="size"
        :state="isHasError(errors)"
        @paste.native="onPaste"
        @keydown.native="onInput"
        :placeholder="placeholder"
        :disabled="disabled"
      ></b-form-textarea>
      <b-form-invalid-feedback v-if="errors.length">
        {{ errors[0] }}
      </b-form-invalid-feedback>
    </ValidationProvider>
  </div>
</template>

<script>
import '@/plugins/vee-validate'
import { validateMixins } from '@/shared/utils'

export default {
  name: 'Textarea',
  props: {
    value: String,
    name: String,
    rules: Array,
    placeholder: String,
    disabled: Boolean,
    validateIf: {
      validator: prop => typeof prop === 'boolean' || prop === null,
      default: true
    },
    size: {
      type: String,
      default: 'md'
    }
  },
  mixins: [validateMixins],
  computed: {
    dataValue: {
      get() {
        return this.$props.value
      },
      set(val) {
        this.$emit('input', val)
      }
    },
    validateRules() {
      return this.validateIf ? this.stringRules(this.rules) : null
    }
  },
  methods: {
    onInput(event) {
      if (event.keyCode === 13) event.preventDefault()
    },
    onPaste(event) {
      event.preventDefault()
      let text = (event.originalEvent || event).clipboardData
        .getData('text')
        .replace(/\r?\n|\r/g, ' ')
      document.execCommand('insertHTML', false, text)
    }
  }
}
</script>

<style lang="scss">
.pf-textarea {
  .was-validated .form-control:invalid,
  .form-control.is-invalid {
    background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='none' stroke='%23dc3545' viewBox='0 0 12 12'%3e%3ccircle cx='6' cy='6' r='4.5'/%3e%3cpath stroke-linejoin='round' d='M5.8 3.6h.4L6 6.5z'/%3e%3ccircle cx='6' cy='8.2' r='.6' fill='%23dc3545' stroke='none'/%3e%3c/svg%3e");
  }
  .form-control::-webkit-scrollbar {
    display: none; /* Hide scrollbar for Chrome, Safari and Opera */
  }
  .form-control {
    -ms-overflow-style: none; /* IE and Edge */
    scrollbar-width: none; /* Firefox */
  }
}
</style>
