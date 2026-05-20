import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export interface UserInfo {
  id: string
  name: string
  email: string
  avatar?: string
}

export const useUserStore = defineStore('user', () => {
  const token = ref<string | null>(null)
  const user = ref<UserInfo | null>(null)

  const isLoggedIn = computed(() => !!token.value)
  const displayName = computed(() => user.value?.name ?? '未登录')

  function login(newToken: string, userInfo?: UserInfo) {
    token.value = newToken
    if (userInfo) user.value = userInfo
  }

  function logout() {
    token.value = null
    user.value = null
  }

  function loadProfile(userInfo: UserInfo) {
    user.value = userInfo
  }

  return {
    token,
    user,
    isLoggedIn,
    displayName,
    login,
    logout,
    loadProfile,
  }
}, {
  persist: {
    pick: ['token'],
  },
})
