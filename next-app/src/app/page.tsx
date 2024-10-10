import { prisma } from '@/lib/prisma'

export default async function Page() {
  const featureCollections = await prisma.featureCollection.findMany()
  
  return (
    <div className='flex flex-col justify-between h-full'>
      <h1 className='text-xl'>Feature Collections</h1>
      {featureCollections.map((fc) => {
        return <p key={fc.id}>{fc.name}</p>
      })}
      <p>The end.</p>
    </div>
  );
}