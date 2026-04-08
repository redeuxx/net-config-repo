<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const devices = ref([])
const searchQuery = ref('')
const loading = ref(false)

const showConfigsModal = ref(false)
const selectedDevice = ref(null)
const deviceConfigs = ref([])
const loadingConfigs = ref(false)

const fetchDevices = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/devices')
    devices.value = res.data
  } catch (err) {
    console.error('Error fetching devices', err)
  } finally {
    loading.value = false
  }
}

const searchDevices = async () => {
  if (!searchQuery.value.trim()) {
    return fetchDevices()
  }
  loading.value = true
  try {
    const res = await axios.get(`/api/devices/search?query=${encodeURIComponent(searchQuery.value)}`)
    devices.value = res.data
  } catch (err) {
    console.error('Error searching devices', err)
  } finally {
    loading.value = false
  }
}

const removeDevice = async (id) => {
  if (!confirm('Are you sure you want to remove this device?')) return
  try {
    await axios.delete(`/api/devices/${id}`)
    fetchDevices()
  } catch (err) {
    alert(err.response?.data?.detail || 'Error removing device')
  }
}

const openConfigs = async (device) => {
  selectedDevice.value = device
  showConfigsModal.value = true
  loadingConfigs.value = true
  deviceConfigs.value = []
  try {
    const res = await axios.get(`/api/devices/${device.id}/configs`)
    deviceConfigs.value = res.data
  } catch (err) {
    console.error('Error fetching configs', err)
  } finally {
    loadingConfigs.value = false
  }
}

const downloadConfig = (configId) => {
  window.open(`/api/configs/${configId}/download`, '_blank')
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  fetchDevices()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Devices Database</h2>
    </div>

    <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6 border dark:border-gray-700">
      <div class="flex justify-between items-center mb-4 border-b dark:border-gray-700 pb-4">
        <form @submit.prevent="searchDevices" class="flex space-x-2 w-full max-w-md">
          <input v-model="searchQuery" type="text" placeholder="Search by IP, name..." class="flex-1 rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm p-2 border sm:text-sm focus:border-blue-500 focus:ring-blue-500" />
          <button type="submit" class="bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-800 dark:text-white font-semibold py-2 px-4 border border-gray-300 dark:border-gray-600 rounded shadow-sm">
            Search
          </button>
          <button type="button" @click="() => { searchQuery = ''; fetchDevices() }" class="bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-800 dark:text-white py-2 px-3 border border-gray-300 dark:border-gray-600 rounded shadow-sm">
            Clear
          </button>
        </form>
      </div>

      <div v-if="loading" class="text-center py-10 text-gray-500 dark:text-gray-400">Loading devices...</div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">ID</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">IP Address</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Hostname</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Type</th>
              <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="dev in devices" :key="dev.id">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{{ dev.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{{ dev.ip }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{{ dev.hostname }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                  {{ dev.device_type }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-3">
                <button @click="openConfigs(dev)" class="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300">Configs</button>
                <button @click="removeDevice(dev.id)" class="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300">Delete</button>
              </td>
            </tr>
            <tr v-if="devices.length === 0">
              <td colspan="5" class="px-6 py-4 text-center text-gray-500 dark:text-gray-400">No devices found.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Configs Modal -->
    <div v-if="showConfigsModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="showConfigsModal = false" aria-hidden="true"></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="inline-block align-bottom bg-white dark:bg-gray-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full border dark:border-gray-700">
          <div class="bg-white dark:bg-gray-800 px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white border-b dark:border-gray-700 pb-2" id="modal-title">
                  Config History: {{ selectedDevice?.ip }}
                </h3>
                
                <div class="mt-4">
                  <div v-if="loadingConfigs" class="text-center py-4 text-gray-500 dark:text-gray-400">Loading configurations...</div>
                  <div v-else-if="deviceConfigs.length === 0" class="text-center py-4 text-gray-500 dark:text-gray-400">No configurations found.</div>
                  <ul v-else class="divide-y divide-gray-200 dark:divide-gray-700 max-h-96 overflow-y-auto">
                    <li v-for="conf in deviceConfigs" :key="conf.id" class="py-3 flex justify-between items-center pr-2">
                      <div>
                        <p class="text-sm font-medium text-gray-900 dark:text-white">Version ID: {{ conf.id }}</p>
                        <p class="text-sm text-gray-500 dark:text-gray-400">Saved on: {{ formatDate(conf.timestamp) }}</p>
                      </div>
                      <button @click="downloadConfig(conf.id)" class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                        Download .txt
                      </button>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 dark:bg-gray-900/50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button type="button" @click="showConfigsModal = false" class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 dark:border-gray-600 shadow-sm px-4 py-2 bg-white dark:bg-gray-800 text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>