/// <reference types="vite/client" />

declare module 'pinia-plugin-persistedstate' {
  import type { PiniaPluginContext } from 'pinia'
  export default function (context: PiniaPluginContext): void
}
