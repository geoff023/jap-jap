export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

interface ErrorBody {
  detail?: string | { msg: string }[]
}

export async function parseErrorMessage(response: Response): Promise<string> {
  try {
    const body: ErrorBody = await response.json()
    if (typeof body.detail === 'string') return body.detail
    if (Array.isArray(body.detail)) return body.detail.map((d) => d.msg).join(', ')
  } catch {
    // response had no JSON body
  }
  return `Request failed with status ${response.status}`
}
