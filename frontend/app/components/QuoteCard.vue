<template>
  <div class="bg-white p-6 rounded-lg shadow hover:shadow-lg transition flex flex-col h-full border border-gray-100">
    <div v-if="quote.image_url" class="mb-4 rounded overflow-hidden aspect-video bg-gray-50 flex items-center justify-center relative">
        <img :src="quote.image_url" :alt="quote.author" class="w-full h-full object-cover">
    </div>
    <div class="flex-grow">
      <p class="text-xl font-serif mb-4 text-gray-800 leading-relaxed">"{{ quote.text }}"</p>
    </div>
    <div class="flex justify-between items-center text-sm text-gray-600 mt-4 pt-4 border-t border-gray-100">
      <span class="font-bold text-gray-900">— {{ quote.author }}</span>
      <a :href="quote.link" target="_blank" class="text-blue-600 hover:text-blue-800 font-medium hover:underline">
        Source
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Quote {
  text: string
  author: string
  link: string
  image_url?: string | null
}

defineProps<{
  quote: Quote
}>()
</script>
