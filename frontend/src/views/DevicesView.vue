<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
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
  if (!searchQuery.value.trim()) return fetchDevices()
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
  diffSelected.value = []
  diffResult.value = []
  viewingConfigId.value = null
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

// --- View single config ---
const viewingConfigId = ref(null)
const viewingConfigText = ref('')
const loadingConfigText = ref(false)

const viewConfig = async (configId) => {
  if (viewingConfigId.value === configId) {
    viewingConfigId.value = null
    viewingConfigText.value = ''
    return
  }
  viewingConfigId.value = configId
  loadingConfigText.value = true
  viewingConfigText.value = ''
  try {
    const res = await axios.get(`/api/configs/${configId}`)
    viewingConfigText.value = res.data.config_text
  } catch (err) {
    viewingConfigText.value = 'Error loading config.'
  } finally {
    loadingConfigText.value = false
  }
}

// --- Diff ---
const diffSelected = ref([])   // array of up to 2 config ids
const diffResult = ref([])     // array of {type, line}
const loadingDiff = ref(false)

const toggleDiffSelect = (configId) => {
  const idx = diffSelected.value.indexOf(configId)
  if (idx !== -1) {
    diffSelected.value.splice(idx, 1)
    diffResult.value = []
  } else if (diffSelected.value.length < 2) {
    diffSelected.value.push(configId)
    diffResult.value = []
  }
}

const canSelectForDiff = (configId) =>
  diffSelected.value.includes(configId) || diffSelected.value.length < 2

// LCS-based line diff
function computeDiff(textA, textB) {
  const a = textA.split('\n')
  const b = textB.split('\n')
  const m = a.length, n = b.length

  // Build LCS table
  const lcs = Array.from({ length: m + 1 }, () => new Int32Array(n + 1))
  for (let i = 1; i <= m; i++)
    for (let j = 1; j <= n; j++)
      lcs[i][j] = a[i-1] === b[j-1] ? lcs[i-1][j-1] + 1 : Math.max(lcs[i-1][j], lcs[i][j-1])

  // Backtrack
  const result = []
  let i = m, j = n
  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && a[i-1] === b[j-1]) {
      result.unshift({ type: 'same', line: a[i-1] })
      i--; j--
    } else if (j > 0 && (i === 0 || lcs[i][j-1] >= lcs[i-1][j])) {
      result.unshift({ type: 'added', line: b[j-1] })
      j--
    } else {
      result.unshift({ type: 'removed', line: a[i-1] })
      i--
    }
  }
  return result
}

const compareConfigs = async () => {
  if (diffSelected.value.length !== 2) return
  loadingDiff.value = true
  diffResult.value = []
  try {
    const [resA, resB] = await Promise.all([
      axios.get(`/api/configs/${diffSelected.value[0]}`),
      axios.get(`/api/configs/${diffSelected.value[1]}`),
    ])
    diffResult.value = computeDiff(resA.data.config_text, resB.data.config_text)
  } catch (err) {
    console.error('Error loading configs for diff', err)
  } finally {
    loadingDiff.value = false
  }
}

const diffStats = computed(() => ({
  added: diffResult.value.filter(l => l.type === 'added').length,
  removed: diffResult.value.filter(l => l.type === 'removed').length,
}))

// --- Per-device config fetch ---
const deviceFetchStates = ref({})  // { [deviceId]: { status: 'idle'|'fetching'|'done'|'error', message: '' } }

const getDeviceFetchState = (deviceId) => deviceFetchStates.value[deviceId] || { status: 'idle', message: '' }

const fetchDevice = async (dev) => {
  if (getDeviceFetchState(dev.id).status === 'fetching') return
  deviceFetchStates.value[dev.id] = { status: 'fetching', message: '' }
  try {
    const res = await axios.post(`/api/devices/${dev.id}/fetch`)
    const jobId = res.data.job_id
    const poll = setInterval(async () => {
      try {
        const jobRes = await axios.get(`/api/jobs/fetch/${jobId}`)
        const job = jobRes.data
        if (job.status === 'COMPLETED') {
          clearInterval(poll)
          deviceFetchStates.value[dev.id] = { status: 'done', message: 'Saved.' }
          setTimeout(() => { deviceFetchStates.value[dev.id] = { status: 'idle', message: '' } }, 5000)
        } else if (job.status === 'FAILED') {
          clearInterval(poll)
          deviceFetchStates.value[dev.id] = { status: 'error', message: job.message || 'Failed.' }
          setTimeout(() => { deviceFetchStates.value[dev.id] = { status: 'idle', message: '' } }, 8000)
        }
      } catch {
        clearInterval(poll)
        deviceFetchStates.value[dev.id] = { status: 'error', message: 'Polling error.' }
        setTimeout(() => { deviceFetchStates.value[dev.id] = { status: 'idle', message: '' } }, 5000)
      }
    }, 2000)
  } catch (err) {
    deviceFetchStates.value[dev.id] = { status: 'error', message: err.response?.data?.detail || 'Failed to start.' }
    setTimeout(() => { deviceFetchStates.value[dev.id] = { status: 'idle', message: '' } }, 5000)
  }
}

// --- Actions dropdown ---
const openDropdownId = ref(null)

const toggleDropdown = (id) => {
  openDropdownId.value = openDropdownId.value === id ? null : id
}

const closeDropdown = () => {
  openDropdownId.value = null
}

const handleDocumentClick = () => closeDropdown()

const formatDate = (dateString) => new Date(dateString).toLocaleString()

onMounted(() => {
  fetchDevices()
  document.addEventListener('click', handleDocumentClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick)
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
          <button type="submit" class="bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-800 dark:text-white font-semibold py-2 px-4 border border-gray-300 dark:border-gray-600 rounded shadow-sm">Search</button>
          <button type="button" @click="() => { searchQuery = ''; fetchDevices() }" class="bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-800 dark:text-white py-2 px-3 border border-gray-300 dark:border-gray-600 rounded shadow-sm">Clear</button>
        </form>
      </div>

      <div v-if="loading" class="text-center py-10 text-gray-500 dark:text-gray-400">Loading devices...</div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">IP Address</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Hostname</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Type</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="dev in devices" :key="dev.id">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{{ dev.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{{ dev.ip }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{{ dev.hostname }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">{{ dev.device_type }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="inline-flex items-center space-x-2">
                  <!-- Fetch status indicator (shown outside dropdown) -->
                  <span v-if="getDeviceFetchState(dev.id).status === 'fetching'" class="text-xs text-yellow-500 dark:text-yellow-400 animate-pulse">Fetching...</span>
                  <span v-else-if="getDeviceFetchState(dev.id).status === 'done'" class="text-xs text-green-600 dark:text-green-400">Config saved.</span>
                  <span v-else-if="getDeviceFetchState(dev.id).status === 'error'" class="text-xs text-red-500 dark:text-red-400" :title="getDeviceFetchState(dev.id).message">Failed</span>

                  <!-- Dropdown -->
                  <div class="relative" @click.stop>
                    <button @click="toggleDropdown(dev.id)" class="inline-flex items-center space-x-1 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">
                      <span>Actions</span>
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
                    </button>
                    <div v-if="openDropdownId === dev.id" class="absolute right-0 mt-1 w-52 bg-white dark:bg-gray-800 rounded-md shadow-lg z-20 border border-gray-200 dark:border-gray-600 overflow-hidden whitespace-normal">
                      <div class="py-1">
                        <button @click="openConfigs(dev); closeDropdown()" class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">
                          Config History
                        </button>
                        <button
                          @click="fetchDevice(dev); closeDropdown()"
                          :disabled="getDeviceFetchState(dev.id).status === 'fetching'"
                          class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          Fetch latest config
                        </button>
                        <div class="border-t border-gray-200 dark:border-gray-600 my-1"></div>
                        <button @click="removeDevice(dev.id); closeDropdown()" class="w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700">
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </td>
            </tr>
            <tr v-if="devices.length === 0">
              <td colspan="5" class="px-6 py-4 text-center text-gray-500 dark:text-gray-400">No devices found.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Config History Modal -->
    <div v-if="showConfigsModal" class="fixed inset-0 z-50 overflow-y-auto" role="dialog" aria-modal="true">
      <div class="flex items-center justify-center min-h-screen px-4">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75" @click="showConfigsModal = false"></div>
        <div class="relative bg-white dark:bg-gray-800 rounded-lg text-left shadow-xl w-full max-w-5xl border dark:border-gray-700 flex flex-col" style="max-height: 90vh;">

          <!-- Header -->
          <div class="px-6 pt-5 pb-3 border-b dark:border-gray-700 flex justify-between items-center flex-shrink-0">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white">Config History: {{ selectedDevice?.ip }}</h3>
            <div v-if="diffSelected.length === 2" class="flex items-center space-x-3">
              <span class="text-xs text-gray-500 dark:text-gray-400">2 selected</span>
              <button @click="compareConfigs" :disabled="loadingDiff" class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50">
                {{ loadingDiff ? 'Comparing...' : 'Compare' }}
              </button>
              <button @click="diffSelected = []; diffResult = []" class="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200">Clear</button>
            </div>
            <span v-else-if="diffSelected.length === 1" class="text-xs text-gray-500 dark:text-gray-400">Select one more to compare</span>
            <span v-else class="text-xs text-gray-500 dark:text-gray-400">Check up to 2 configs to compare</span>
          </div>

          <!-- Body -->
          <div class="overflow-y-auto flex-1 px-6 py-4">
            <div v-if="loadingConfigs" class="text-center py-8 text-gray-500 dark:text-gray-400">Loading configurations...</div>
            <div v-else-if="deviceConfigs.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">No configurations found.</div>
            <ul v-else class="divide-y divide-gray-200 dark:divide-gray-700">
              <li v-for="conf in deviceConfigs" :key="conf.id" class="py-3">
                <div class="flex justify-between items-center">
                  <div class="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      :checked="diffSelected.includes(conf.id)"
                      :disabled="!canSelectForDiff(conf.id)"
                      @change="toggleDiffSelect(conf.id)"
                      class="h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500 disabled:opacity-30 cursor-pointer disabled:cursor-not-allowed"
                    />
                    <div>
                      <p class="text-sm font-medium text-gray-900 dark:text-white">Version ID: {{ conf.id }}</p>
                      <p class="text-sm text-gray-500 dark:text-gray-400">Saved on: {{ formatDate(conf.timestamp) }}</p>
                    </div>
                  </div>
                  <div class="flex space-x-2">
                    <button @click="viewConfig(conf.id)" class="inline-flex items-center px-3 py-1.5 border text-xs font-medium rounded shadow-sm focus:outline-none"
                      :class="viewingConfigId === conf.id ? 'bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-white border-gray-300 dark:border-gray-500' : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-500 hover:bg-gray-50 dark:hover:bg-gray-600'">
                      {{ viewingConfigId === conf.id ? 'Hide' : 'View' }}
                    </button>
                    <button @click="downloadConfig(conf.id)" class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-white bg-indigo-600 hover:bg-indigo-700">
                      Download
                    </button>
                  </div>
                </div>
                <!-- Inline view -->
                <div v-if="viewingConfigId === conf.id" class="mt-3">
                  <div v-if="loadingConfigText" class="text-sm text-gray-500 dark:text-gray-400 py-2">Loading...</div>
                  <pre v-else class="bg-gray-900 text-gray-100 text-xs font-mono p-4 rounded overflow-auto whitespace-pre" style="max-height: 350px;">{{ viewingConfigText }}</pre>
                </div>
              </li>
            </ul>

            <!-- Diff output -->
            <div v-if="diffResult.length > 0" class="mt-6">
              <div class="flex items-center justify-between mb-3">
                <h4 class="text-sm font-semibold text-gray-900 dark:text-white">
                  Diff — Version {{ diffSelected[0] }} vs Version {{ diffSelected[1] }}
                </h4>
                <div class="flex space-x-3 text-xs">
                  <span class="text-red-600 dark:text-red-400">−{{ diffStats.removed }} removed</span>
                  <span class="text-green-600 dark:text-green-400">+{{ diffStats.added }} added</span>
                </div>
              </div>
              <div class="bg-gray-900 rounded overflow-auto font-mono text-xs" style="max-height: 500px;">
                <table class="w-full border-collapse">
                  <tbody>
                    <tr v-for="(chunk, i) in diffResult" :key="i"
                      :class="{
                        'bg-red-950 text-red-300':   chunk.type === 'removed',
                        'bg-green-950 text-green-300': chunk.type === 'added',
                        'text-gray-400':               chunk.type === 'same',
                      }">
                      <td class="select-none w-6 px-2 text-center opacity-60 border-r border-gray-700"
                        :class="{
                          'text-red-500':   chunk.type === 'removed',
                          'text-green-500': chunk.type === 'added',
                        }">
                        {{ chunk.type === 'removed' ? '−' : chunk.type === 'added' ? '+' : ' ' }}
                      </td>
                      <td class="px-3 py-0.5 whitespace-pre">{{ chunk.line }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="px-6 py-3 border-t dark:border-gray-700 flex justify-end flex-shrink-0">
            <button @click="showConfigsModal = false" class="inline-flex justify-center rounded-md border border-gray-300 dark:border-gray-600 shadow-sm px-4 py-2 bg-white dark:bg-gray-800 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700">
              Close
            </button>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>
