import { api } from './client'

export const AnalyticsAPI = {
  track: (eventType: string, props: any = {}) => api.post('/analytics/track', {}, { params: { event_type: eventType, properties: JSON.stringify(props) } }).catch(()=>{}),
  daily: (days = 30) => api.get('/analytics/daily', { params: { days } }),
  myEvents: () => api.get('/analytics/me/events'),
}
