<script setup lang="ts">
import { Icon } from '@iconify/vue'
import { ref, watch } from 'vue'
import { fetchDepartures } from '@/api'
import type { DeparturesResponse } from '@/api'
import StationCard from '@/components/StationCard.vue'

const query = ref('')
const result = ref<DeparturesResponse | null>(null)
const error = ref<string | null>(null)
const loading = ref(false)

let debounceTimer: ReturnType<typeof setTimeout>

watch(query, (val) => {
  clearTimeout(debounceTimer)
  result.value = null
  error.value = null
  if (val.length < 3) return
  debounceTimer = setTimeout(async () => {
    loading.value = true
    try {
      result.value = await fetchDepartures(val)
    } catch (e: any) {
      error.value = e.message ?? 'Unknown error'
    } finally {
      loading.value = false
    }
  }, 300)
})

function delayBadgeClass(minutes: number) {
  if (minutes === 0) return 'badge badge-success'
  if (minutes <= 5) return 'badge badge-warning'
  return 'badge badge-error'
}

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div class="flex flex-col items-center gap-6 p-6">
    <h1 class="font-bold text-5xl">Lagovia Train Tracker</h1>

    <label class="input w-96">
      <Icon icon="mdi:magnify" class="text-gray-500" />
      <input v-model="query" type="search" required placeholder="Search station…" />
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
      <StationCard v-for="station in result.stations" :key="station.station" :station="station" />
      <p v-if="result.stations.length === 0" class="text-gray-400">
        No stations matched your search.
      </p>
    </template>
  </div>
</template>

<style scoped></style>
