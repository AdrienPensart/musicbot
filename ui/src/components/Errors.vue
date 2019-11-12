<template>
  <p v-if="errors.length">
    <b>Please correct the following error(s):</b>
    <ul>
      <li v-for="error in errors" :key="error.id">{{ error }}</li>
    </ul>
  </p>
</template>
<script>
export default {
  computed : {
    errors: function(){ return this.$store.getters.errors }
  },
}
</script>
