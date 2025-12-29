<template>
  <b-alert
    v-model="showErrorAlert"
    variant="danger"
    dismissible
    v-if="isObject(errorMessages)"
  >
    <strong class="error-messages__tilte">Errors:</strong>
    <div
      class="error-messages__error"
      v-for="([errorKey, errorValue], index) in Object.entries(errorMessages)"
      :key="`errors-${index}`"
    >
      <div class="error-messages__key">{{ errorKey | filterColumnName }}:</div>
      <div v-if="Array.isArray(errorValue)">
        <div
          class="error-messages__value"
          v-for="(error, index) in errorValue"
          :key="`error-${index}`"
        >
          {{ error }}
        </div>
      </div>
      <div v-else class="error-messages__value">{{ errorValue }}</div>
    </div>
  </b-alert>
</template>

<script>
import _ from 'lodash'
import { filterColumnName } from '@/shared/filters'

export default {
  name: 'ErrorMessages',
  props: {
    showErrorAlert: Boolean,
    errorMessages: Object
  },
  computed: {
    isObject() {
      return data => _.isObject(data)
    }
  },
  filters: {
    filterColumnName
  }
}
</script>

<style lang="scss" scoped>
.error-messages {
  color: red;
  margin-bottom: 10px;
  &__tilte {
    text-transform: uppercase;
  }
  &__error {
    display: flex;
  }
  &__value {
    margin-left: 7px;
  }
}
</style>
