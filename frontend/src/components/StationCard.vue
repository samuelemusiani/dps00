<script setup lang="ts">
import { Icon } from '@iconify/vue'
import type { StationDepartures } from '@/api'

const { station } = defineProps<{ station: StationDepartures }>()

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
  <div class="card bg-base-200 shadow w-full max-w-2xl">
    <div class="card-body gap-4">
      <h2 class="card-title">
        <Icon icon="mdi:train-station" />
        {{ station.station }}
      </h2>

      <div v-if="station.departures.length === 0" class="opacity-70 text-sm">
        No departures found.
      </div>

      <table v-else class="table table-sm w-full">
        <thead>
          <tr>
            <th class="w-px">Train</th>
            <th>Destination</th>
            <th class="w-px text-right">Scheduled</th>
            <th class="w-px text-right">Delay</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="dep in station.departures" :key="dep.train_number">
            <td class="font-semibold whitespace-nowrap">{{ dep.train_number }}</td>
            <td>{{ dep.destination }}</td>
            <td class="text-right whitespace-nowrap">
              {{ formatTime(dep.scheduled_time) }}
            </td>
            <td class="text-right whitespace-nowrap">
              <span :class="delayBadgeClass(dep.delay_minutes)" class="min-w-28">
                {{ dep.delay_minutes === 0 ? 'On time' : `+${dep.delay_minutes} min` }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped></style>
