<script setup>
import { ref } from 'vue'
import axios from 'axios'

const newDevice = ref({
  ip: '',
  username: '',
  password: '',
  enable_password: '',
  device_type: ''
})
const actionMessage = ref('')

const addDevice = async () => {
  if (!newDevice.value.ip) return
  actionMessage.value = 'Adding device, please wait...'
  try {
    const res = await axios.post('/api/devices', newDevice.value)
    actionMessage.value = res.data.message
    newDevice.value = { ip: '', username: '', password: '', enable_password: '', device_type: '' }
  } catch (err) {
    actionMessage.value = err.response?.data?.detail || 'Error adding device'
  }
}

const triggerFetchAll = async () => {
  actionMessage.value = 'Starting fetch configs job...'
  try {
    const res = await axios.post('/api/jobs/fetch', {})
    actionMessage.value = res.data.message
  } catch (err) {
    actionMessage.value = err.response?.data?.detail || 'Error starting fetch job'
  }
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h2>
      <div v-if="actionMessage" class="text-sm font-medium text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 px-4 py-2 rounded">
        {{ actionMessage }}
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Add Device Card -->
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6 border dark:border-gray-700">
        <h2 class="text-lg font-semibold mb-4 border-b dark:border-gray-700 pb-2 dark:text-white">Add Device</h2>
        <form @submit.prevent="addDevice" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">IP Address</label>
            <input v-model="newDevice.ip" type="text" required class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border" placeholder="192.168.1.1" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Username</label>
              <input v-model="newDevice.username" type="text" class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm p-2 border" placeholder="(optional)" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Password</label>
              <input v-model="newDevice.password" type="password" class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm p-2 border" placeholder="(optional)" />
            </div>
          </div>
          <div>
            <button type="submit" class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
              Add Device
            </button>
          </div>
        </form>
      </div>

      <!-- Global Actions -->
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6 border dark:border-gray-700 space-y-6">
        <div>
          <h2 class="text-lg font-semibold mb-4 border-b dark:border-gray-700 pb-2 dark:text-white">Global Actions</h2>
          <button @click="triggerFetchAll" class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
            Fetch All Configs
          </button>
          <p class="text-sm text-gray-500 dark:text-gray-400 mt-3 text-center">
            Starts a background job to fetch configurations from all reachable devices in the database.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>