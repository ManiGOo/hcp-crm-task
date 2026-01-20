import { Routes, Route } from 'react-router-dom';

import LogInteractionScreen from './pages/LogInteractionScreen';
import Interactions from './pages/Interactions';

function App() {
  return (
    <Routes>
      <Route path="/" element={<LogInteractionScreen />} />
      <Route path="/interactions" element={<Interactions />} />
    </Routes>
  );
}

export default App;