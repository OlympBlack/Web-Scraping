<template>
  <div class="w-full bg-gray-300 rounded h-4">
    <div
      class="bg-green-500 h-4 rounded transition-all duration-300"
      :style="{ width: percent + '%' }"
    ></div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ percent: number }>()
</script>
