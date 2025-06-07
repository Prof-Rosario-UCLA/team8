import { useCallback, useRef } from "react"
import { debounce } from "lodash"

export function useResumeItemSync(itemId: number) {
  const patch = async (field: string, value: string) => {
    await fetch(`/api/resume/item/update/${itemId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ [field]: value }),
    })
  }

  // note: useref used here to avoid recreating debounced function per render
  const debouncedPatch = useRef(
    debounce((field: string, value: string) => {
      patch(field, value)
    }, 500)
  ).current

  const updateField = useCallback((field: string, value: string) => {
    debouncedPatch(field, value)
  }, [])

  return { updateField }
}
