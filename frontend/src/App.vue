<script setup>
import { ref, onMounted, onUnmounted, provide } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const isDark = ref(false)

// Global Scan Jobs State
const scanJobs = ref([])
let pollingInterval = null

const fetchScanJobs = async () => {
  try {
    const res = await axios.get('/api/jobs/scan')
    scanJobs.value = res.data

    const isRunning = scanJobs.value.some(job => job.status === 'RUNNING')
    if (isRunning) {
      if (pollingInterval) clearTimeout(pollingInterval)
      pollingInterval = setTimeout(fetchScanJobs, 2000)
    } else if (pollingInterval) {
      clearTimeout(pollingInterval)
      pollingInterval = null
    }
  } catch (err) {
    console.error('Error fetching scan jobs', err)
  }
}

provide('scanJobs', scanJobs)
provide('fetchScanJobs', fetchScanJobs)

// Global Fetch Jobs State
const fetchJobs = ref([])
let fetchPollingInterval = null

const refreshFetchJobs = async () => {
  try {
    const res = await axios.get('/api/jobs/fetch')
    fetchJobs.value = res.data

    const isRunning = fetchJobs.value.some(job => job.status === 'RUNNING')
    if (isRunning) {
      if (fetchPollingInterval) clearTimeout(fetchPollingInterval)
      fetchPollingInterval = setTimeout(refreshFetchJobs, 2000)
    } else if (fetchPollingInterval) {
      clearTimeout(fetchPollingInterval)
      fetchPollingInterval = null
    }
  } catch (err) {
    console.error('Error fetching fetch jobs', err)
  }
}

provide('fetchJobs', fetchJobs)
provide('refreshFetchJobs', refreshFetchJobs)

// Settings Modal State
const showSettingsModal = ref(false)
const maxConfigs = ref(10)
const defaultUsername = ref('')
const defaultPassword = ref('')
const defaultEnablePassword = ref('')
const savingSettings = ref(false)
const actionMessage = ref('')

const toggleDark = () => {
  isDark.value = !isDark.value
  if (isDark.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

const openSettings = async () => {
  try {
    const res = await axios.get('/api/settings')
    maxConfigs.value = res.data.max_configs_per_device
    defaultUsername.value = res.data.default_username
    defaultPassword.value = res.data.default_password
    defaultEnablePassword.value = res.data.default_enable_password
    showSettingsModal.value = true
  } catch (err) {
    console.error('Error fetching settings', err)
    actionMessage.value = 'Failed to connect to backend API. Please ensure the server is running.'
    setTimeout(() => actionMessage.value = '', 5000)
  }
}

const saveSettings = async () => {
  savingSettings.value = true
  try {
    await axios.post('/api/settings', { 
      max_configs_per_device: maxConfigs.value,
      default_username: defaultUsername.value,
      default_password: defaultPassword.value,
      default_enable_password: defaultEnablePassword.value
    })
    showSettingsModal.value = false
    actionMessage.value = 'Settings updated successfully'
    setTimeout(() => actionMessage.value = '', 3000)
  } catch (err) {
    console.error('Error saving settings', err)
  } finally {
    savingSettings.value = false
  }
}

onMounted(() => {
  if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    isDark.value = true
    document.documentElement.classList.add('dark')
  } else {
    isDark.value = false
    document.documentElement.classList.remove('dark')
  }
})
</script>

<template>
  <div class="min-h-screen bg-gray-100 dark:bg-gray-900 transition-colors duration-200 text-gray-800 dark:text-gray-200 font-sans flex flex-col md:flex-row">
    
    <!-- Sidebar Navigation -->
    <aside class="w-full md:w-64 bg-white dark:bg-gray-800 border-r dark:border-gray-700 shadow flex flex-col">
      <div class="p-6 border-b dark:border-gray-700 flex justify-between items-center">
        <h1 class="text-xl font-bold text-gray-900 dark:text-white">net-config-repo</h1>
        
        <!-- Dark Mode Toggle Mobile -->
        <button @click="toggleDark" class="md:hidden text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 p-2 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
          <svg v-if="!isDark" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        </button>
      </div>

      <nav class="flex-1 p-4 space-y-2">
        <router-link to="/" class="block px-4 py-2 rounded-md font-medium" :class="[ $route.path === '/' ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/50 dark:text-blue-400' : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700' ]">
          Dashboard
        </router-link>
        <router-link to="/devices" class="block px-4 py-2 rounded-md font-medium" :class="[ $route.path === '/devices' ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/50 dark:text-blue-400' : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700' ]">
          Devices
        </router-link>
        <router-link to="/devices/add" class="block pl-8 pr-4 py-1.5 rounded-md text-sm font-medium" :class="[ $route.path === '/devices/add' ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/50 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700' ]">
          Add Device
        </router-link>
        <router-link to="/devices/fetch" class="flex justify-between items-center pl-8 pr-4 py-1.5 rounded-md text-sm font-medium" :class="[ $route.path === '/devices/fetch' ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/50 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700' ]">
          <span>Fetch Configs</span>
          <span v-if="fetchJobs.some(j => j.status === 'RUNNING')" class="flex h-3 w-3 relative">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
          </span>
        </router-link>
        <router-link to="/devices/scan" class="flex justify-between items-center pl-8 pr-4 py-1.5 rounded-md text-sm font-medium" :class="[ $route.path === '/devices/scan' ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/50 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700' ]">
          <span>Scan Network</span>
          <span v-if="scanJobs.some(j => j.status === 'RUNNING')" class="flex h-3 w-3 relative">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
          </span>
        </router-link>
        <router-link to="/logs" class="block px-4 py-2 rounded-md font-medium" :class="[ $route.path === '/logs' ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/50 dark:text-blue-400' : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700' ]">
          System Logs
        </router-link>
      </nav>

      <div class="p-4 border-t dark:border-gray-700 flex justify-between items-center space-x-2">
        <button @click="openSettings" class="flex-1 flex justify-center items-center px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          Settings
        </button>

        <button @click="toggleDark" class="hidden md:flex justify-center items-center p-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors" title="Toggle Dark Mode">
          <svg v-if="!isDark" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        </button>
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="flex-1 p-6 lg:p-8 overflow-y-auto flex flex-col">
      <div v-if="actionMessage" class="mb-4 text-sm font-medium text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 px-4 py-2 rounded shadow-sm flex justify-between items-center">
        {{ actionMessage }}
        <button @click="actionMessage = ''" class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200">x</button>
      </div>

      <div class="flex-1">
        <router-view></router-view>
      </div>

      <footer class="mt-8 pt-4 border-t dark:border-gray-700 text-center text-xs text-gray-400 dark:text-gray-500">
        <a href="https://github.com/redeuxx/net-config-repo" target="_blank" rel="noopener noreferrer" class="hover:text-gray-600 dark:hover:text-gray-300 transition-colors">net-config-repo</a>
      </footer>
    </main>

    <!-- Settings Modal -->
    <div v-if="showSettingsModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="showSettingsModal = false" aria-hidden="true"></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="inline-block align-bottom bg-white dark:bg-gray-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full border dark:border-gray-700">
          <div class="bg-white dark:bg-gray-800 px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white" id="modal-title">Global Settings</h3>
                <div class="mt-4 space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Max Config Versions per Device</label>
                    <input type="number" v-model.number="maxConfigs" min="1" class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm p-2 border focus:border-blue-500 focus:ring-blue-500 sm:text-sm" />
                    <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">Older configurations will be automatically deleted to save space.</p>
                  </div>
                  
                  <div class="border-t dark:border-gray-700 pt-4">
                    <h4 class="text-md font-medium text-gray-900 dark:text-white mb-2">Default Global Credentials</h4>
                    <p class="text-xs text-gray-500 dark:text-gray-400 mb-3">Used for background scans and config fetches if device-specific credentials are not provided.</p>
                    
                    <div class="space-y-3">
                      <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Default Username</label>
                        <input type="text" v-model="defaultUsername" class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm p-2 border focus:border-blue-500 focus:ring-blue-500 sm:text-sm" />
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Default Password</label>
                        <input type="password" v-model="defaultPassword" class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm p-2 border focus:border-blue-500 focus:ring-blue-500 sm:text-sm" />
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Default Enable Password</label>
                        <input type="password" v-model="defaultEnablePassword" class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm p-2 border focus:border-blue-500 focus:ring-blue-500 sm:text-sm" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 dark:bg-gray-900/50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse border-t dark:border-gray-700">
            <button type="button" @click="saveSettings" :disabled="savingSettings" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none sm:ml-3 sm:w-auto sm:text-sm">
              Save
            </button>
            <button type="button" @click="showSettingsModal = false" class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 dark:border-gray-600 shadow-sm px-4 py-2 bg-white dark:bg-gray-800 text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm">
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>