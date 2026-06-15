<script setup lang="ts">
import { Icon } from '@iconify/vue'
import { computed, ref, watch } from 'vue'
import { fetchDepartures } from '@/api'
import type { DeparturesResponse } from '@/api'
import StationCard from '@/components/StationCard.vue'

const query = ref('')
const result = ref<DeparturesResponse | null>(null)
const error = ref<string | null>(null)
const loading = ref(false)
const executionTime = ref(0)

let debounceTimer: ReturnType<typeof setTimeout>

watch(query, (val) => {
  search(val)
})

function search(query: string) {
  clearTimeout(debounceTimer)
  result.value = null
  error.value = null
  if (query.length < 3) return
  debounceTimer = setTimeout(async () => {
    const now = performance.now()

    loading.value = true
    try {
      result.value = await fetchDepartures(query)
    } catch (e) {
      if (e instanceof Error) {
        error.value = e.message ?? 'Unknown error'
      } else {
        error.value = 'Unknown error'
      }
    } finally {
      loading.value = false
    }
    executionTime.value = performance.now() - now
  }, 300)
}

const totalDepartures = computed(() => {
  if (!result.value) return 0
  return result.value.stations.reduce((sum, station) => sum + station.departures.length, 0)
})

function triggerSearch() {
  if (query.value.length < 3) {
    error.value = 'Please enter at least 3 characters to search.'
    result.value = null
    return
  }
  search(query.value)
}
</script>

<template>
  <div class="flex flex-col items-center gap-6 p-6">
    <h1 class="font-bold text-5xl">Lagovia Train Tracker</h1>

    <label class="input w-96">
      <Icon icon="mdi:magnify" class="text-gray-500" />
      <input
        v-model="query"
        type="search"
        required
        placeholder="Search station…"
        @keydown.enter.prevent="triggerSearch"
      />
    </label>

    <div v-if="loading" class="flex items-center gap-2 text-gray-500">
      <span class="loading loading-spinner loading-sm" />
      Searching…
    </div>

    <div v-else-if="error" role="alert" class="alert alert-error max-w-xl w-full">
      <Icon icon="mdi:alert-circle-outline" class="text-xl shrink-0" />
      <span>{{ error }}</span>
    </div>

    <template v-else-if="result">
      <div>
        <p class="text-gray-500">
          Found
          {{ result.stations.length }} station{{ result.stations.length > 1 ? 's' : '' }} and
          {{ totalDepartures }} departure{{ totalDepartures > 1 ? 's' : '' }} in
          {{ executionTime }} ms.
        </p>
      </div>
      <StationCard v-for="station in result.stations" :key="station.station" :station="station" />
      <p v-if="result.stations.length === 0" class="text-gray-400">
        No stations matched your search.
      </p>
    </template>
  </div>
</template>

<style scoped></style>
