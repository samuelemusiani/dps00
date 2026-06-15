<script setup lang="ts">
import { Icon } from '@iconify/vue'
</script>

<template>
  <div class="flex flex-col items-center gap-4">
    <h1 class="font-bold text-5xl">Lagovia Train Tracker</h1>
    <label class="input">
      <Icon icon="mdi:magnify" class="text-gray-500" />
      <input type="search" required placeholder="Search" />
    </label>
  </div>
</template>

<style scoped></style>
