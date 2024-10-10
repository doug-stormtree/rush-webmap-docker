import type { Metadata } from 'next'

// These styles apply to every route in the application
import './global.css'

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
      <body className='h-dvh'>
        {children}
      </body>
    </html>
  )
}