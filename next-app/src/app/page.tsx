import { prisma } from '@/lib/prisma'

export default async function Page() {
  const featureCollections = await prisma.featureCollection.findMany()
  
  return (
    <div>
      <h1>Feature Collections</h1>
      {featureCollections.map((fc) => {
        return <p key={fc.id}>{fc.name}</p>
      })}
    </div>
  );
}