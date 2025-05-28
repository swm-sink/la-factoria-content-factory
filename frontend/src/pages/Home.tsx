import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div className="relative isolate">
      <div className="mx-auto max-w-7xl px-6 py-24 sm:py-32 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
            AI Content Factory
          </h1>
          <p className="mt-6 text-lg leading-8 text-gray-600">
            Generate high-quality educational content with AI. Create study guides, podcasts, and more with just a few clicks.
          </p>
          <div className="mt-10 flex items-center justify-center gap-x-6">
            <Link
              to="/generate"
              className="rounded-md bg-primary-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600"
            >
              Get started
            </Link>
            <Link to="/history" className="text-sm font-semibold leading-6 text-gray-900">
              View history <span aria-hidden="true">→</span>
            </Link>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl lg:text-center">
          <h2 className="text-base font-semibold leading-7 text-primary-600">Features</h2>
          <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            Everything you need to create educational content
          </p>
        </div>
        <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
          <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-3">
            {features.map((feature) => (
              <div key={feature.name} className="flex flex-col">
                <dt className="flex items-center gap-x-3 text-base font-semibold leading-7 text-gray-900">
                  {feature.name}
                </dt>
                <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-gray-600">
                  <p className="flex-auto">{feature.description}</p>
                </dd>
              </div>
            ))}
          </dl>
        </div>
      </div>
    </div>
  )
}

const features = [
  {
    name: 'Content Generation',
    description: 'Generate comprehensive study guides, podcasts, and educational content using advanced AI models.',
  },
  {
    name: 'Audio Creation',
    description: 'Convert your content into high-quality audio using state-of-the-art text-to-speech technology.',
  },
  {
    name: 'Content History',
    description: 'Access your previously generated content and audio files anytime, anywhere.',
  },
] 