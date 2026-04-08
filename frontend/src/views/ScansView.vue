<script setup>
import { ref, inject, watch, nextTick } from 'vue'
import axios from 'axios'

const scanCidr = ref('')
const actionMessage = ref('')

// Inject the globally managed state and fetch function from App.vue
const scanJobs = inject('scanJobs')
const fetchScanJobs = inject('fetchScanJobs')

const terminalRef = ref(null)

// Auto-scroll terminal when it updates
watch(scanJobs, async () => {
  await nextTick()
  if (terminalRef.value) {
    terminalRef.value.scrollTop = terminalRef.value.scrollHeight
  }
}, { deep: true })

const triggerScan = async () => {
  if (!scanCidr.value) return
  actionMessage.value = 'Starting scan...'
  try {
    const res = await axios.post('/api/jobs/scan', { cidr: scanCidr.value })
    actionMessage.value = res.data.message
    scanCidr.value = ''
    if (fetchScanJobs) fetchScanJobs()
  } catch (err) {
    actionMessage.value = err.response?.data?.detail || 'Error starting scan'
  }
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Network Scans</h2>
      <div v-if="actionMessage" class="text-sm font-medium text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 px-4 py-2 rounded">
        {{ actionMessage }}
      </div>
    </div>

    <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6 border dark:border-gray-700">
      <h2 class="text-lg font-semibold mb-4 border-b dark:border-gray-700 pb-2 dark:text-white">Scan Network</h2>
      <div class="flex space-x-2 mb-4">
        <input v-model="scanCidr" type="text" class="block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm p-2 border focus:border-green-500 focus:ring-green-500" placeholder="e.g. 10.0.0.0/24" />
        <button @click="triggerScan" class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
          Start Scan
        </button>
      </div>
      
      <!-- Latest Scan Job Display -->
      <div class="mt-6" v-if="scanJobs && scanJobs.length > 0">
        <h3 class="text-md font-semibold mb-3 text-gray-800 dark:text-gray-200">Latest Scan Progress</h3>
        
        <div class="p-4 border dark:border-gray-700 rounded-md bg-gray-50 dark:bg-gray-900/50">
          <div class="flex justify-between items-center mb-2">
            <span class="font-medium text-gray-900 dark:text-white">{{ scanJobs[0].cidr }}</span>
            <span :class="{
              'text-yellow-600 dark:text-yellow-400 font-semibold animate-pulse': scanJobs[0].status === 'RUNNING',
              'text-green-600 dark:text-green-400 font-semibold': scanJobs[0].status === 'COMPLETED',
              'text-red-600 dark:text-red-400 font-semibold': scanJobs[0].status === 'FAILED'
            }">
              {{ scanJobs[0].status }}
            </span>
          </div>
          
          <div v-if="scanJobs[0].status === 'RUNNING' && scanJobs[0].progress_total > 0" class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 mb-3">
            <div class="bg-blue-600 h-2.5 rounded-full transition-all duration-500" :style="{ width: `${(scanJobs[0].progress_current / scanJobs[0].progress_total) * 100}%` }"></div>
          </div>

          <!-- Terminal Output Window -->
          <div class="mt-3 bg-gray-900 text-gray-100 font-mono text-xs p-3 rounded overflow-y-auto" style="max-height: 300px;" ref="terminalRef">
            <pre class="whitespace-pre-wrap">{{ scanJobs[0].detailed_log || 'Waiting for output...' }}</pre>
          </div>
        </div>
      </div>

      <div v-else class="mt-6 text-gray-500 dark:text-gray-400 text-sm italic">
        No recent scans found. Enter a CIDR above to start a network sweep.
      </div>
    </div>
  </div>
</template>