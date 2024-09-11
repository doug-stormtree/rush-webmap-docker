import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'RUSH',
  description: 'Resilient Urban Systems & Habitats',
}

export default function RootLayout({
  // Layouts must accept a children prop.
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang='en'>
      <body>{children}</body>
    </html>
  )
}