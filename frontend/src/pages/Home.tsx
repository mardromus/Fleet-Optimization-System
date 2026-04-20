import MapComponent from '../components/Map/Map';
import Dashboard from '../components/Dashboard/Dashboard';

const Home = () => {
  return (
    <div className="flex h-screen w-screen overflow-hidden">
      <div className="flex-1 relative">
        <MapComponent />
      </div>
      <Dashboard />
    </div>
  );
};

export default Home;
