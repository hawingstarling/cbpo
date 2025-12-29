<template>
    <b-dropdown right v-if="hasPermission(permissions[typeDropdown].share) || hasPermission(permissions[typeDropdown].delete)" size="sm" text="Small">
    <template #button-content>
      <i class="fa fa-cog"/> Manage
    </template>
    <b-dropdown-item v-if="hasPermission(permissions[typeDropdown].edit)" text="Small" size="sm" @click="openEditModal()"><i class="fa fa-pencil"></i>Edit</b-dropdown-item>
    <b-dropdown-item v-if="hasPermission(permissions[typeDropdown].share)" text="Small" size="sm" @click="openShareModal()"><i class="fa fa-share-alt-square mr-1"></i>Share</b-dropdown-item>
    <b-dropdown-item v-if="hasPermission(permissions[typeDropdown].delete)" text="Small" size="sm" @click="openDeleteConfirmModal()"><i class="fa fa-trash-o mr-1"></i>Delete</b-dropdown-item>
  </b-dropdown>
</template>

<script>
import PermissionsMixin from '@/components/common/PermissionsMixin'
import { convertedPermissions as permissions } from '@/shared/utils'

export default {
  name: 'ManageDropdown',
  mixins: [ PermissionsMixin ],
  props: {
    typeDropdown: String
  },
  data() {
    return {
      permissions
    }
  },
  methods: {
    openShareModal() {
      this.$emit('openShareModal')
    },
    openDeleteConfirmModal() {
      this.$emit('openDeleteConfirmModal')
    },
    openEditModal() {
      this.$emit('openEditModal')
    }
  }
}
</script>
