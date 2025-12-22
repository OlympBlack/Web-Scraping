<template>
  <div class="min-h-screen bg-gray-50 py-10 px-4">
    <div class="max-w-5xl mx-auto">
      <h1 class="text-4xl font-bold text-center mb-8 text-gray-900 tracking-tight">Citations Scraper</h1>
      
      <!-- Control Panel -->
      <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-8">
        <div class="flex flex-col md:flex-row gap-4 mb-4">
          <input
            v-model="topic"
            placeholder="Sujet (ex: motivation, love, nature, technology)"
            class="flex-1 p-4 border border-gray-200 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition"
            @keyup.enter="startScraping"
          />
          <button
            @click="startScraping"
            :disabled="loading"
            class="bg-black text-white px-8 py-4 rounded-lg font-medium hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center justify-center min-w-[160px]"
          >
            <span v-if="loading" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              En cours...
            </span>
            <span v-else>Lancer</span>
          </button>
          
          <button
            v-if="loading"
            @click="stopScraping"
            class="bg-red-600 text-white px-8 py-4 rounded-lg font-medium hover:bg-red-700 transition flex items-center justify-center"
          >
            Arrêter
          </button>
        </div>

        <!-- Progress Bar and Stats -->
        <div v-if="loading || progress > 0" class="space-y-2">
            <div class="flex justify-between text-sm font-medium text-gray-600">
                <span>Progression: {{ progress }} citations trouvées</span>
                <span v-if="total > 0">~{{ displayedPercentage.toFixed(1) }}%</span>
            </div>
            <div class="w-full bg-gray-100 rounded-full h-3 overflow-hidden">
                <div 
                    class="bg-black h-3 rounded-full transition-all duration-300 ease-out"
                    :style="{ width: `${displayedPercentage}%` }"
                ></div>
            </div>
            <p v-if="loading" class="text-xs text-center text-gray-400 animate-pulse">Récupération des données en temps réel...</p>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="mt-4 p-4 bg-red-50 text-red-600 rounded-lg border border-red-100 flex items-center">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            {{ error }}
        </div>
      </div>

      <!-- Results Actions -->
      <div v-if="quotes.length > 0 && !loading" class="flex justify-end gap-3 mb-6">
        <button @click="downloadJSON" class="flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm font-medium transition">
            <span class="mr-2">Example.json</span> Télécharger JSON
        </button>
        <button @click="downloadCSV" class="flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm font-medium transition">
             <span class="mr-2">Example.csv</span> Télécharger CSV
        </button>
      </div>

      <!-- Results Grid -->
      <div v-if="quotes.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <QuoteCard
          v-for="(quote, index) in quotes"
          :key="index"
          :quote="quote"
        />
      </div>
      
      <!-- Empty State -->
      <div v-else-if="!loading && !error" class="text-center py-20 text-gray-400">
        <p class="text-lg">Entrez un sujet pour commencer à extraire des citations.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import QuoteCard from "~/components/QuoteCard.vue"

interface Quote {
  text: string
  author: string
  link: string
  image_url?: string | null
  progress?: number
  total?: number
}

const topic = ref("")
const quotes = ref<Quote[]>([])
const loading = ref(false)
const error = ref("")
const progress = ref(0)
const total = ref(0)
const displayedPercentage = ref(0)

let abortController: AbortController | null = null

const startScraping = async () => {
  if (!topic.value.trim()) {
    error.value = "Veuillez entrer un sujet"
    return
  }

  // Reset state
  error.value = ""
  loading.value = true
  quotes.value = []
  progress.value = 0
  displayedPercentage.value = 0
  total.value = 30  // Start with an estimated "horizon" of one page
  
  // Create new controller for this request
  abortController = new AbortController()
  const signal = abortController.signal
  
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  try {
    const response = await fetch(`${apiBase}/api/scrape?topic=${encodeURIComponent(topic.value)}`, {
      signal
    })

    if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`)
    }

    if (!response.body) {
        throw new Error("Pas de réponse du serveur")
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ""

    while (true) {
      const { done, value } = await reader.read()
      
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split("\n")
      
      // Process all complete lines
      buffer = lines.pop() || "" // Keep incomplete line in buffer

      for (const line of lines) {
        if (!line.trim()) continue
        
        try {
          const data = JSON.parse(line)
          
          if (data.error) {
            error.value = data.error
            loading.value = false
            return
          }

          // Handle progress update
          // Ignore backend total to avoid premature 100%
          
          if (data.done) {
              loading.value = false
              total.value = progress.value // Snap to final count
              progress.value = total.value
              displayedPercentage.value = 100
              return
          }

          if (data.text) {
              quotes.value.push(data)
              progress.value = quotes.value.length
              
              // Dynamic Horizon: If we are getting close to the estimated total, extend it.
              if (progress.value >= total.value * 0.8) {
                  total.value += 30
              }

              // --- Monotonic Asymptotic Logic ---
              const rawPercent = (progress.value / total.value) * 100
              let nextPercent = displayedPercentage.value

              if (rawPercent > displayedPercentage.value) {
                  // Standard case: we have room to grow
                  // If we are nearing 100%, dampen the approach (Asymptotic)
                  if (rawPercent > 95) {
                      // Move only 10% of the remaining distance to rawPercent to slow down
                      nextPercent += (rawPercent - displayedPercentage.value) * 0.1
                  } else {
                     // Normal catch-up
                     nextPercent = rawPercent
                  }
              } else {
                  // Horizon expanded (rawPercent dropped), but we MUST NOT go back.
                  // Artificial micro-increment to show "aliveness"
                  nextPercent += 0.1
              }

              // Hard cap at 99.5% until fully done
              if (nextPercent > 99.5) nextPercent = 99.5
              
              displayedPercentage.value = nextPercent
          }

        } catch (parseError) {
          console.warn("Erreur de parsing JSON:", parseError, line)
        }
      }
    }

  } catch (e: any) {
    if (e.name === 'AbortError') {
      console.log('Scraping annulé')
    } else {
      console.error(e)
      error.value = e.message || "Impossible de récupérer les données"
    }
  } finally {
    loading.value = false
    abortController = null
  }
}

const stopScraping = () => {
  if (abortController) {
    abortController.abort()
    loading.value = false
  }
}

const downloadJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(quotes.value, null, 2))
    const downloadAnchorNode = document.createElement('a')
    downloadAnchorNode.setAttribute("href", dataStr)
    downloadAnchorNode.setAttribute("download", `citations-${topic.value}.json`)
    document.body.appendChild(downloadAnchorNode)
    downloadAnchorNode.click()
    downloadAnchorNode.remove()
}

const downloadCSV = () => {
    if (quotes.value.length === 0) return

    const headers = ["Auteur", "Citation", "Lien", "Image"]
    const rows = quotes.value.map(q => [
        `"${q.author.replace(/"/g, '""')}"`,
        `"${q.text.replace(/"/g, '""')}"`,
        `"${q.link}"`,
        `"${q.image_url || ''}"`
    ])
    
    const csvContent = "data:text/csv;charset=utf-8," 
        + headers.join(",") + "\n" 
        + rows.map(e => e.join(",")).join("\n")

    const encodedUri = encodeURI(csvContent)
    const link = document.createElement("a")
    link.setAttribute("href", encodedUri)
    link.setAttribute("download", `citations-${topic.value}.csv`)
    document.body.appendChild(link)
    link.click()
    link.remove()
}
</script>
