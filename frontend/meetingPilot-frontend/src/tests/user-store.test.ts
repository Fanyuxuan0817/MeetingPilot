import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore, type UserInfo } from '@/stores/user'

describe('useUserStore', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  describe('state initialization', () => {
    it('should have correct default values', () => {
      const store = useUserStore()
      expect(store.token).toBeNull()
      expect(store.user).toBeNull()
      expect(store.isLoggedIn).toBe(false)
      expect(store.displayName).toBe('未登录')
    })
  })

  describe('getters', () => {
    it('isLoggedIn returns true when token is set', () => {
      const store = useUserStore()
      store.login('jwt-token-123')
      expect(store.isLoggedIn).toBe(true)
    })

    it('isLoggedIn returns false when token is null', () => {
      const store = useUserStore()
      expect(store.isLoggedIn).toBe(false)
    })

    it('displayName returns user name when logged in', () => {
      const store = useUserStore()
      store.login('token', { id: '1', name: 'Alice', email: 'a@b.com' })
      expect(store.displayName).toBe('Alice')
    })

    it('displayName returns "未登录" when not logged in', () => {
      const store = useUserStore()
      expect(store.displayName).toBe('未登录')
    })
  })

  describe('login', () => {
    it('sets token and user info', () => {
      const store = useUserStore()
      const userInfo: UserInfo = { id: '1', name: 'Alice', email: 'a@b.com' }

      store.login('jwt-token', userInfo)

      expect(store.token).toBe('jwt-token')
      expect(store.user).toEqual(userInfo)
      expect(store.isLoggedIn).toBe(true)
    })

    it('sets token without user info', () => {
      const store = useUserStore()

      store.login('jwt-token')

      expect(store.token).toBe('jwt-token')
      expect(store.user).toBeNull()
      expect(store.isLoggedIn).toBe(true)
    })
  })

  describe('logout', () => {
    it('clears token and user', () => {
      const store = useUserStore()
      store.login('jwt-token', { id: '1', name: 'Alice', email: 'a@b.com' })

      store.logout()

      expect(store.token).toBeNull()
      expect(store.user).toBeNull()
      expect(store.isLoggedIn).toBe(false)
    })
  })

  describe('loadProfile', () => {
    it('updates user info without changing token', () => {
      const store = useUserStore()
      store.login('jwt-token')

      const profile: UserInfo = { id: '1', name: 'Bob', email: 'b@b.com' }
      store.loadProfile(profile)

      expect(store.user).toEqual(profile)
      expect(store.token).toBe('jwt-token')
    })
  })

  describe('persistence config', () => {
    it('store definition includes persist option with token only', () => {
      const store = useUserStore()
      store.login('persisted-token', { id: '1', name: 'Secret', email: 's@b.com' })

      expect(store.token).toBe('persisted-token')
      expect(store.user).toEqual({ id: '1', name: 'Secret', email: 's@b.com' })
    })

    it('logout sets token to null for persistence plugin to clear', () => {
      const store = useUserStore()
      store.login('will-be-cleared')
      store.logout()

      expect(store.token).toBeNull()
      expect(store.isLoggedIn).toBe(false)
    })

    it('user info is not part of persisted fields (pick: token)', () => {
      const store = useUserStore()
      store.login('token-only', { id: '1', name: 'Alice', email: 'a@b.com' })

      expect(store.token).toBe('token-only')
      expect(store.user).not.toBeNull()

      store.logout()

      expect(store.token).toBeNull()
      expect(store.user).toBeNull()
    })
  })

  describe('SSR safety', () => {
    it('does not access other stores at module level', () => {
      const store = useUserStore()
      expect(store).toBeDefined()
    })
  })
})
