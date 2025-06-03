import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import axios from 'axios'

interface ContentRequest {
  topic: string
  content_type: string
  target_audience: string
  length: string
}

interface ContentResponse {
  content: {
    outline: string
    podcast_script: string
    study_guide: string
    one_pager_summaries: string[]
    detailed_reading_materials: string[]
    faqs: { question: string; answer: string }[]
    flashcards: { front: string; back: string }[]
    reading_guide_questions: string[]
  }
  audio_url?: string
}

export default function ContentGenerator() {
  const [formData, setFormData] = useState<ContentRequest>({
    topic: '',
    content_type: 'study_guide',
    target_audience: 'students',
    length: 'medium',
  })

  const generateContent = useMutation<ContentResponse, Error, ContentRequest>({
    mutationFn: async (data: ContentRequest) => {
      const response = await axios.post('/api/generate-content', data)
      return response.data
    }
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    generateContent.mutate(formData)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-3xl">
        <form onSubmit={handleSubmit} className="space-y-8 divide-y divide-gray-200">
          <div className="space-y-8 divide-y divide-gray-200">
            <div>
              <div>
                <h3 className="text-base font-semibold leading-6 text-gray-900">Generate Content</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Fill out the form below to generate educational content.
                </p>
              </div>

              <div className="mt-6 grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                <div className="sm:col-span-4">
                  <label htmlFor="topic" className="block text-sm font-medium leading-6 text-gray-900">
                    Topic
                  </label>
                  <div className="mt-2">
                    <input
                      type="text"
                      name="topic"
                      id="topic"
                      value={formData.topic}
                      onChange={handleChange}
                      className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                      required
                    />
                  </div>
                </div>

                <div className="sm:col-span-3">
                  <label htmlFor="content_type" className="block text-sm font-medium leading-6 text-gray-900">
                    Content Type
                  </label>
                  <div className="mt-2">
                    <select
                      id="content_type"
                      name="content_type"
                      value={formData.content_type}
                      onChange={handleChange}
                      className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                    >
                      <option value="study_guide">Study Guide</option>
                      <option value="podcast">Podcast</option>
                      <option value="summary">Summary</option>
                    </select>
                  </div>
                </div>

                <div className="sm:col-span-3">
                  <label htmlFor="target_audience" className="block text-sm font-medium leading-6 text-gray-900">
                    Target Audience
                  </label>
                  <div className="mt-2">
                    <select
                      id="target_audience"
                      name="target_audience"
                      value={formData.target_audience}
                      onChange={handleChange}
                      className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                    >
                      <option value="students">Students</option>
                      <option value="professionals">Professionals</option>
                      <option value="general">General Audience</option>
                    </select>
                  </div>
                </div>

                <div className="sm:col-span-3">
                  <label htmlFor="length" className="block text-sm font-medium leading-6 text-gray-900">
                    Length
                  </label>
                  <div className="mt-2">
                    <select
                      id="length"
                      name="length"
                      value={formData.length}
                      onChange={handleChange}
                      className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                    >
                      <option value="short">Short</option>
                      <option value="medium">Medium</option>
                      <option value="long">Long</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-5">
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={generateContent.isPending}
                className="ml-3 inline-flex justify-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600"
              >
                {generateContent.isPending ? 'Generating...' : 'Generate Content'}
              </button>
            </div>
          </div>
        </form>

        {generateContent.isError && (
          <div className="mt-6 rounded-md bg-red-50 p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>{generateContent.error?.message}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {generateContent.isSuccess && (
          <div className="mt-6">
            <h3 className="text-lg font-medium leading-6 text-gray-900">Generated Content</h3>
            <div className="mt-4 space-y-4">
              <div>
                <h4 className="text-sm font-medium text-gray-900">Outline</h4>
                <p className="mt-1 text-sm text-gray-500">{generateContent.data.content.outline}</p>
              </div>
              {generateContent.data.audio_url && (
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Audio</h4>
                  <audio controls className="mt-1">
                    <source src={generateContent.data.audio_url} type="audio/mpeg" />
                    Your browser does not support the audio element.
                  </audio>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
