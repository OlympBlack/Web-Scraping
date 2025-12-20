<template>
  <div class="p-6 max-w-4xl mx-auto">
    <!-- Formulaire -->
    <div class="mb-6">
      <input
        v-model="topic"
        placeholder="Ex: motivation, love, success"
        class="w-full p-3 border rounded mb-3"
      />
      <button
        @click="startScraping"
        :disabled="loading"
        class="w-full bg-black text-white py-3 rounded hover:bg-gray-800 disabled:opacity-50"
      >
        {{ loading ? "Scraping en cours..." : "Lancer le scraping" }}
      </button>
    </div>

    <!-- Erreur -->
    <div v-if="error" class="text-red-600 text-center mb-4">
      {{ error }}
    </div>

    <!-- Loader -->
    <div v-if="loading" class="text-center mb-4">
      ⏳ Récupération des citations...
    </div>

    <!-- Résultat -->
    <div class="grid md:grid-cols-2 gap-4">
      <QuoteCard
        v-for="(quote, index) in quotes"
        :key="index"
        :quote="quote"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import QuoteCard from "~/components/QuoteCard.vue"

const topic = ref("")
const quotes = ref<Quote[]>([])
const loading = ref(false)
const error = ref("")

interface Quote {
  text: string
  author: string
  link: string
}

interface ApiResponse {
  count: number
  data: Quote[]
}

const startScraping = async () => {
  if (!topic.value.trim()) {
    error.value = "Veuillez entrer un sujet"
    return
  }

  error.value = ""
  loading.value = true
  quotes.value = []

  try {
    // normaliser le topic pour BrainyQuote
    const cleanTopic = topic.value.trim().toLowerCase().replace(/\s+/g, "-")

    const { data, error: fetchError } = await useFetch<ApiResponse>(
      `http://127.0.0.1:8000/api/scrape?topic=${cleanTopic}`
    )

    if (fetchError.value) {
      throw new Error("Erreur backend")
    }

    quotes.value = data.value?.data ?? []

    if (quotes.value.length === 0) {
      error.value = "Aucune citation trouvée pour ce sujet"
    }
  } catch (e) {
    console.error(e)
    error.value = "Impossible de récupérer les données"
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Styles spécifique */
</style>
