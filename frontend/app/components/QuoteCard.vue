<template>
  <div class="bg-white p-4 rounded shadow">
    <p class="italic mb-3">"{{ quote.text }}"</p>
    <p class="font-semibold text-right">— {{ quote.author }}</p>

    <a
      :href="quote.link"
      target="_blank"
      class="text-sm text-blue-600 hover:underline"
    >
      Voir la citation
    </a>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  quote: {
    text: string
    author: string
    link: string
  }
}>()
</script>
