interface HighlightedTextProps {
  text: string
  searchTerm: string
}

export function HighlightedText({ text, searchTerm }: HighlightedTextProps) {
  if (!searchTerm) return <span>{text}</span>

  const regex = new RegExp(`(${searchTerm})`, "gi")
  const parts = text.split(regex)

  return (
    <>
      {parts.map((part, i) =>
        regex.test(part) ? (
          <mark key={i} className="bg-yellow-200 rounded px-0.5">
            {part}
          </mark>
        ) : (
          <span key={i}>{part}</span>
        ),
      )}
    </>
  )
}
