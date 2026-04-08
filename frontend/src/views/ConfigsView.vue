<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const configs = ref([])
const loading = ref(false)
const searchQuery = ref('')

const showViewModal = ref(false)
const selectedConfig = ref(null)
const loadingDetail = ref(false)

const fetchConfigs = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/configs')
    configs.value = res.data
  } catch (err) {
    console.error('Error fetching configs', err)
  } finally {
    loading.value = false
  }
}

const viewConfig = async (configId) => {
  showViewModal.value = true
  loadingDetail.value = true
  selectedConfig.value = null
  try {
    const res = await axios.get(`/api/configs/${configId}`)
    selectedConfig.value = res.data
  } catch (err) {
    console.error('Error fetching config detail', err)
  } finally {
    loadingDetail.value = false
  }
}

const downloadConfig = (configId) => {
  window.open(`/api/configs/${configId}/download`, '_blank')
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}

const filteredConfigs = () => {
  if (!searchQuery.value.trim()) return configs.value
  const q = searchQuery.value.toLowerCase()
  return configs.value.filter(c => 
    c.device_ip.toLowerCase().includes(q) || 
    c.device_hostname.toLowerCase().includes(q)
  )
}

onMounted(() => {
  fetchConfigs()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Recent Configs</h2>
      <button @click="fetchConfigs" class="bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 py-2 px-4 border border-gray-300 dark:border-gray-600 rounded shadow-sm">
        Refresh
      </button>
    </div>

    <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6 border dark:border-gray-700">
      <div class="mb-4">
        <input v-model="searchQuery" type="text" placeholder="Filter by IP or hostname..." class="w-full max-w-md rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm p-2 border sm:text-sm focus:border-blue-500 focus:ring-blue-500" />
      </div>

      <div v-if="loading" class="text-center py-10 text-gray-500 dark:text-gray-400">Loading configurations...</div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Device IP</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Hostname</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Timestamp</th>
              <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="conf in filteredConfigs()" :key="conf.id">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{{ conf.device_ip }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{{ conf.device_hostname }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{{ formatDate(conf.timestamp) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-3">
                <button @click="viewConfig(conf.id)" class="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300">View</button>
                <button @click="downloadConfig(conf.id)" class="text-indigo-600 dark:text-indigo-400 hover:text-indigo-900 dark:hover:text-indigo-300">Download</button>
              </td>
            </tr>
            <tr v-if="filteredConfigs().length === 0">
              <td colspan="4" class="px-6 py-4 text-center text-gray-500 dark:text-gray-400">No matching configurations found.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- View Modal -->
    <div v-if="showViewModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="showViewModal = false" aria-hidden="true"></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="inline-block align-bottom bg-white dark:bg-gray-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full border dark:border-gray-700">
          <div class="bg-white dark:bg-gray-800 px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white border-b dark:border-gray-700 pb-2 flex justify-between" id="modal-title">
                  <span>Configuration: {{ selectedConfig?.device_ip || 'Loading...' }}</span>
                  <span class="text-sm font-normal text-gray-500">{{ selectedConfig ? formatDate(selectedConfig.timestamp) : '' }}</span>
                </h3>
                
                <div class="mt-4">
                  <div v-if="loadingDetail" class="text-center py-10 text-gray-500 dark:text-gray-400">Fetching configuration text...</div>
                  <div v-else-if="selectedConfig" class="bg-gray-900 text-gray-100 p-4 rounded-md overflow-x-auto max-h-[60vh]">
                    <pre class="text-xs whitespace-pre">{{ selectedConfig.config_text }}</pre>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 dark:bg-gray-900/50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse border-t dark:border-gray-700">
            <button type="button" @click="showViewModal = false" class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 dark:border-gray-600 shadow-sm px-4 py-2 bg-white dark:bg-gray-800 text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm">
              Close
            </button>
            <button v-if="selectedConfig" type="button" @click="downloadConfig(selectedConfig.id)" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none sm:ml-3 sm:w-auto sm:text-sm">
              Download .txt
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>