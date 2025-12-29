<template>
  <div>
    <div>
      Profile Name
      <b-form-input v-model="itemEdit.profile_name"></b-form-input>
    </div>
    <div>
      Profile Link
      <b-form-input v-model="itemEdit.profile_id_link"></b-form-input>
    </div>
  </div>
</template>

<script>
import _ from 'lodash'

export default {
  name: 'EditProfileModal',
  props: {
    item: Object
  },
  data() {
    return {
      itemEdit: {}
    }
  },
  mounted() {
    this.itemEdit = _.cloneDeep(this.$props.item)
  }
}
</script>
