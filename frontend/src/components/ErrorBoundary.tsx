import { Component, ReactNode } from 'react'

export default class ErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean, error?: any }> {
  constructor(props: any) {
    super(props)
    this.state = { hasError: false }
  }
  static getDerivedStateFromError(error: any) {
    return { hasError: true, error }
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 text-center">
          <h2 className="text-xl font-bold">Something went wrong</h2>
          <p className="text-gray-500 text-sm mt-2">{String(this.state.error)}</p>
          <button onClick={() => window.location.reload()} className="mt-4 px-4 py-2 bg-[#FF4458] text-white rounded-full">Reload</button>
        </div>
      )
    }
    return this.props.children
  }
}
