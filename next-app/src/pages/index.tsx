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

const Home: React.FC<Props> = ({ featureCollections }) => {
  return (
    <div>
      <h1>Users</h1>
      <ul>
        {featureCollections.map((fc) => (
          <li key={fc.id}>{fc.email}</li>
        ))}
      </ul>
    </div>
  );
};

export const getServerSideProps: GetServerSideProps = async () => {
  const featureCollections = await prisma.featureCollection.findMany();
  console.log(Object.keys(featureCollections));
  //console.log("feature collections  awd aw d: " + JSON.stringify(featureCollections, null, 4));
  return {
    props: { users: usersWithSerializedDates },
  };
};

export default Home;
