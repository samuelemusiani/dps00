export interface Departure {
  train_number: string
  destination: string
  scheduled_time: string
  delay_minutes: number
}

export interface StationDepartures {
  station: string
  departures: Departure[]
}

export interface DeparturesResponse {
  stations: StationDepartures[]
}

export interface ErrorResponse {
  error: string
  detail: string
}

export async function fetchDepartures(q: string): Promise<DeparturesResponse> {
  const response = await fetch(`/departures?q=${encodeURIComponent(q)}`)
  if (!response.ok) {
    const err: ErrorResponse = await response.json()
    throw new Error(err.detail ?? err.error)
  }
  return response.json()
}
