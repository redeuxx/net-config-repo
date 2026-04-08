<script setup>
import { ref, inject, watch, nextTick } from 'vue'
import axios from 'axios'

const fetchJobs = inject('fetchJobs')
const refreshFetchJobs = inject('refreshFetchJobs')

const actionMessage = ref('')
const terminalRef = ref(null)

watch(fetchJobs, async () => {
  await nextTick()
  if (terminalRef.value) {
    terminalRef.value.scrollTop = terminalRef.value.scrollHeight
  }
}, { deep: true })

const triggerFetch = async () => {
  actionMessage.value = 'Starting fetch...'
  try {
    const res = await axios.post('/api/jobs/fetch', {})
    actionMessage.value = res.data.message
    if (refreshFetchJobs) refreshFetchJobs()
  } catch (err) {
    actionMessage.value = err.response?.data?.detail || 'Error starting fetch job'
  }
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Fetch Configs</h2>
      <div v-if="actionMessage" class="text-sm font-medium text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 px-4 py-2 rounded">
        {{ actionMessage }}
      </div>
    </div>

    <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6 border dark:border-gray-700">
      <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
        Fetches the running configuration from all devices in the database. Runs concurrently in the background.
      </p>
      <button @click="triggerFetch" :disabled="fetchJobs && fetchJobs.some(j => j.status === 'RUNNING')" class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed">
        Fetch All Configs
      </button>

      <div class="mt-6" v-if="fetchJobs && fetchJobs.length > 0">
        <h3 class="text-md font-semibold mb-3 text-gray-800 dark:text-gray-200">Latest Job Progress</h3>

        <div class="p-4 border dark:border-gray-700 rounded-md bg-gray-50 dark:bg-gray-900/50">
          <div class="flex justify-between items-center mb-2">
            <span class="font-medium text-gray-900 dark:text-white">{{ fetchJobs[0].message || 'Running...' }}</span>
            <span :class="{
              'text-yellow-600 dark:text-yellow-400 font-semibold animate-pulse': fetchJobs[0].status === 'RUNNING',
              'text-green-600 dark:text-green-400 font-semibold': fetchJobs[0].status === 'COMPLETED',
              'text-red-600 dark:text-red-400 font-semibold': fetchJobs[0].status === 'FAILED'
            }">
              {{ fetchJobs[0].status }}
            </span>
          </div>

          <div v-if="fetchJobs[0].progress_total > 0" class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 mb-3">
            <div class="bg-indigo-600 h-2.5 rounded-full transition-all duration-500" :style="{ width: `${(fetchJobs[0].progress_current / fetchJobs[0].progress_total) * 100}%` }"></div>
          </div>

          <div class="mt-3 bg-gray-900 text-gray-100 font-mono text-xs p-3 rounded overflow-y-auto" style="max-height: 300px;" ref="terminalRef">
            <pre class="whitespace-pre-wrap">{{ fetchJobs[0].detailed_log || 'Waiting for output...' }}</pre>
          </div>
        </div>
      </div>

      <div v-else class="mt-6 text-gray-500 dark:text-gray-400 text-sm italic">
        No fetch jobs yet. Click the button above to start.
      </div>
    </div>
  </div>
</template>
