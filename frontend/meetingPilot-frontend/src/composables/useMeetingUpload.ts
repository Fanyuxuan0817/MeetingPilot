import { ref } from 'vue'
import { useMeetingStore } from '@/stores/meeting'
import { useTaskPolling } from './useTaskPolling'
import type { UploadMeetingParams } from '@/api/meetings'
import { MeetingStatus } from '@/types'

export function useMeetingUpload() {
  const meetingStore = useMeetingStore()
  const { startPolling, stopPolling, isPolling } = useTaskPolling()

  const uploadProgress = ref(0)
  const isUploading = ref(false)
  const uploadError = ref<string | null>(null)

  async function upload(file: File, metadata: Omit<UploadMeetingParams, 'file'>) {
    isUploading.value = true
    uploadError.value = null
    uploadProgress.value = 0

    try {
      const job = await meetingStore.uploadAudio({
        file,
        title: metadata.title,
        description: metadata.description,
        language: metadata.language,
        enable_speaker_diarization: metadata.enable_speaker_diarization,
      })

      uploadProgress.value = 50

      startPolling(async () => {
        const jobsRes = await meetingStore.fetchMeetingJobs(job.meeting_id)
        const currentJob = jobsRes.jobs.find((j) => j.id === job.job_id)

        if (currentJob) {
          uploadProgress.value = 50 + Math.floor(currentJob.progress * 0.5)
        }

        const isDone =
          !jobsRes.jobs.some((j) => j.id === job.job_id && j.status === 'running') &&
          !jobsRes.jobs.some((j) => j.id === job.job_id && j.status === 'pending')

        if (isDone) {
          uploadProgress.value = 100
          await meetingStore.loadMeetings()
          return true
        }

        return false
      })

      return job
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : '上传失败'
      uploadError.value = message
      throw err
    } finally {
      isUploading.value = false
    }
  }

  function reset() {
    uploadProgress.value = 0
    isUploading.value = false
    uploadError.value = null
    stopPolling()
  }

  return {
    uploadProgress,
    isUploading,
    uploadError,
    isPolling,
    upload,
    reset,
  }
}
