// pages/index.tsx
import { GetServerSideProps } from 'next';
import { prisma } from '../lib/prisma';

interface FeatureCollection {
  id: number;
  name: string;
  crs: JSON | null;
  features: JSON;
  createdAt: string;
}

interface Props {
  featureCollections: FeatureCollection[];
}

const Home: React.FC<Props> = (props) => {
  return (
    <div>
      <h1>Users</h1>
      {props.featureCollections.map((fc: FeatureCollection) => {
        return <p key={fc.id}>{fc.name}</p>
      })}
    </div>
  );
};

export const getServerSideProps: GetServerSideProps = async () => {
  const featureCollections = await prisma.featureCollection.findMany()

  return {
    props: { featureCollections: [
      { ...featureCollections[0], createdAt: featureCollections[0].createdAt.toISOString() }
    ] },
  };
};

export default Home;