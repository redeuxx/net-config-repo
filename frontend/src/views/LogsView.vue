<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const logs = ref([])
const loading = ref(false)

const fetchLogs = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/logs')
    logs.value = res.data
  } catch (err) {
    console.error('Error fetching logs', err)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  fetchLogs()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white">System Logs</h2>
      <button @click="fetchLogs" class="bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 py-2 px-4 border border-gray-300 dark:border-gray-600 rounded shadow-sm flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Refresh
      </button>
    </div>

    <div class="bg-white dark:bg-gray-800 shadow rounded-lg border dark:border-gray-700 overflow-hidden">
      <div v-if="loading" class="text-center py-10 text-gray-500 dark:text-gray-400">Loading logs...</div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider w-48">Timestamp</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider w-24">Level</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Message</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <template v-for="log in logs" :key="log.id">
              <tr class="hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 align-top">
                  {{ formatDate(log.timestamp) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium align-top">
                  <span :class="{
                    'text-red-600 dark:text-red-400': log.level === 'ERROR',
                    'text-yellow-600 dark:text-yellow-400': log.level === 'WARNING',
                    'text-blue-600 dark:text-blue-400': log.level === 'INFO'
                  }">
                    {{ log.level }}
                  </span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-900 dark:text-gray-200">
                  <p class="font-medium">{{ log.message }}</p>
                  <pre v-if="log.details" class="mt-2 text-xs text-red-500 dark:text-red-400 bg-red-50 dark:bg-red-900/20 p-2 rounded overflow-x-auto whitespace-pre-wrap">{{ log.details }}</pre>
                </td>
              </tr>
            </template>
            <tr v-if="logs.length === 0">
              <td colspan="3" class="px-6 py-4 text-center text-gray-500 dark:text-gray-400">No logs recorded yet.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>